"""
Plugin to inspect Echo transfer protocols. A protocol is a csv file with one transfer per line, e.g.

    ,Sample ID,Source plate,Source well,Destination plate,Destination well,Transfer Volume,Source Plate Type
    0,C0001_10.0,PB000164,A1,PB000146,A1,2.5,384PP_DMSO2

(see processes/protocols and devices/uppsala/echo/sila_server/tests/test_data). The column names of the Echo
software variants are accepted as well (e.g., "Source Plate Barcode", "Destination Plate Name", "Transfer volume").
The optional columns "Source Plate Type" and "Destination Plate Type" give the Echo labware names of the plates (e.g.
384PP_DMSO2, Corning_384w_3784). They become the plate types in the process, which are announced to the Echo when the
plates are handed over.

After loading, the plates and their transfers are shown as a bipartite graph (like create_summary.py of the Echo
server): source plates left, destination plates right, edges labeled with the number of transfers. Clicking a source
plate shows its layout with the volume leaving each well, each used well in its own rainbow color. Clicking a
destination plate shows its layout with the volume arriving in each well. Wells receiving liquid from the selected
source plate get the color of the source well it comes from. Volumes are in nL.
Below the graph, every plate is listed with its current device and the device it is brought to (see
TARGET_DEVICES). Both are preselected: the current device from the status database (Fridge for source and Hotel2 for
destination plates if it is unknown), the target is the current device.

"Add Process" creates a pythonLab process (based on BasicProcess) containing all transfers: each source plate is
surveyed in the Echo, then every destination plate receiving liquid from it gets its transfers. Afterwards, all plates
go to their targets. Plates known to the database start where it says. The others start in the first free slots of
the chosen device.
"""
import base64
import csv
import io
import re
import traceback
from dataclasses import dataclass, field
from pathlib import PurePath

import plotly.graph_objects as go
from dash import callback_context, dcc, html, no_update
from dash.dependencies import ALL, Input, Output, State
from dash_extensions.enrich import DashProxy

from laborchestrator.database_integration import StatusDBDummyImplementation
from laborchestrator.gui.plugins import PluginInterface
from laborchestrator.logging_manager import StandardLogger as Logger
from laborchestrator.structures import ContainerInfo

# accepted column names (compared case-insensitively), as in create_summary.py of the Echo server
COLUMNS = {
    "source": ("Source plate", "Source Plate Barcode", "Source Plate Name"),
    "source_well": ("Source well",),
    "dest": ("Destination plate", "Destination Plate Name", "Destination Plate Barcode"),
    "dest_well": ("Destination well",),
    "volume": ("Transfer Volume",),
}
# optional columns with the Echo labware name of the plate
TYPE_COLUMNS = {"source": "Source Plate Type", "dest": "Destination Plate Type"}
WELL_PATTERN = re.compile(r"([A-Za-z]{1,2})0*(\d+)")
# standard plate formats: number of wells -> (rows, columns)
PLATE_FORMATS = {96: (8, 12), 384: (16, 24), 1536: (32, 48)}
# colors of create_summary.py
SOURCE_FILL, DEST_FILL, NODE_BORDER, EDGE_COLOR = "#d9f2e6", "#fde7d9", "#4f5d75", "#2d3748"
SELECTED_BORDER = "#d62728"
# wells with a transfer that is not between the selected plates
OTHER_WELL_COLOR = "#e2e8f0"
# devices (names of the platform config) the plates can be brought to
TARGET_DEVICES = ["Cytomat1", "Cytomat2", "Hotel2", "Fridge"]
# device name -> attribute of BasicProcess (for the target and the start position)
DEVICE_ATTRIBUTES = {"Cytomat1": "incubator1", "Cytomat2": "incubator2", "Hotel2": "hotel2", "Fridge": "fridge"}
# current device of plates the database does not know
DEFAULT_DEVICES = {"source": "Fridge", "destination": "Hotel2"}
# the processes are named <prefix><number>
PROCESS_NAME_PREFIX = "EchoProcess"
# plate types (as in the existing Echo processes) if the protocol does not give one
DEFAULT_PLATE_TYPES = {"source": "384PP_DMSO2", "dest": "384PP_Dest"}


@dataclass(frozen=True)
class Transfer:
    source: str
    source_well: str
    dest: str
    dest_well: str
    volume: float


@dataclass
class EchoProtocol:
    filename: str
    transfers: list[Transfer] = field(default_factory=list)
    plate_types: dict[str, str] = field(default_factory=dict)  # plate barcode -> plate type (if given)
    errors: list[str] = field(default_factory=list)

    @property
    def sources(self) -> list[str]:
        return sorted({t.source for t in self.transfers})

    @property
    def destinations(self) -> list[str]:
        return sorted({t.dest for t in self.transfers})

    def transfers_of(self, source: str | None = None, dest: str | None = None) -> list[Transfer]:
        return [t for t in self.transfers
                if (source is None or t.source == source) and (dest is None or t.dest == dest)]


def normalize_well(well: str) -> str | None:
    """'a01' -> 'A1', None if it is no well name"""
    match = WELL_PATTERN.fullmatch(well.strip())
    if not match or int(match.group(2)) == 0:
        return None
    return f"{match.group(1).upper()}{int(match.group(2))}"


def well_position(well: str) -> tuple[int, int]:
    """'B3' -> (1, 2), zero based row and column"""
    match = WELL_PATTERN.fullmatch(well)
    letters = match.group(1)
    row = 0
    for letter in letters:
        row = row * 26 + ord(letter) - ord("A") + 1
    return row - 1, int(match.group(2)) - 1


def row_name(row: int) -> str:
    """0 -> 'A', 26 -> 'AA'"""
    return chr(ord("A") + row) if row < 26 else chr(ord("A") + row // 26 - 1) + chr(ord("A") + row % 26)


def plate_format(wells: list[str], plate_type: str = "") -> tuple[int, int]:
    """(rows, columns) of the plate, taken from its plate type (e.g. 384PP_DMSO2) or the smallest fitting format"""
    match = re.search(r"1536|384|96", plate_type)
    if match:
        return PLATE_FORMATS[int(match.group())]
    positions = [well_position(well) for well in wells]
    for rows, columns in PLATE_FORMATS.values():
        if all(row < rows and column < columns for row, column in positions):
            return rows, columns
    return max(row for row, _ in positions) + 1, max(column for _, column in positions) + 1


def parse_protocol(filename: str, text: str) -> EchoProtocol:
    protocol = EchoProtocol(filename=filename)
    reader = csv.DictReader(io.StringIO(text))
    by_lower = {(name or "").strip().lower(): name for name in reader.fieldnames or []}
    columns = {}
    for key, candidates in COLUMNS.items():
        found = [by_lower[c.lower()] for c in candidates if c.lower() in by_lower]
        if found:
            columns[key] = found[0]
        else:
            protocol.errors.append(f"Could not find a column {' or '.join(repr(c) for c in candidates)}.")
    if protocol.errors:
        return protocol
    type_columns = {key: by_lower[name.lower()] for key, name in TYPE_COLUMNS.items() if name.lower() in by_lower}
    # the header is line 1
    for number, line in enumerate(reader, start=2):
        values = {key: (line.get(column) or "").strip() for key, column in columns.items()}
        if not any(values.values()):
            continue
        source_well, dest_well = normalize_well(values["source_well"]), normalize_well(values["dest_well"])
        try:
            volume = float(values["volume"])
        except ValueError:
            volume = None
        if not values["source"] or not values["dest"]:
            protocol.errors.append(f"Line {number}: a plate barcode is missing.")
        elif source_well is None or dest_well is None:
            protocol.errors.append(f"Line {number}: '{values['source_well']}' or '{values['dest_well']}' is no well.")
        elif volume is None or volume < 0:
            protocol.errors.append(f"Line {number}: '{values['volume']}' is no transfer volume.")
        else:
            protocol.transfers.append(Transfer(values["source"], source_well, values["dest"], dest_well, volume))
            for key, column in type_columns.items():
                plate, plate_type = values[key], (line.get(column) or "").strip()
                if not plate_type:
                    continue
                known = protocol.plate_types.setdefault(plate, plate_type)
                if known != plate_type:
                    protocol.errors.append(f"Line {number}: {plate} has the plate type {plate_type}, but {known} "
                                           f"before.")
    if not protocol.transfers and not protocol.errors:
        protocol.errors.append("The file contains no transfers.")
    return protocol


def rainbow(count: int) -> list[str]:
    """count distinct colors from red to violet, light enough for black text"""
    return [f"hsl({round(270 * i / max(count - 1, 1))}, 85%, 65%)" for i in range(count)]


def source_well_colors(protocol: EchoProtocol, source: str) -> dict[str, str]:
    """well -> color for all wells of the source plate liquid is taken from (ordered by row, then column)"""
    wells = sorted({t.source_well for t in protocol.transfers_of(source=source)}, key=well_position)
    return dict(zip(wells, rainbow(len(wells))))


def format_volume(volume: float) -> str:
    return f"{volume:g}"


def create_graph(protocol: EchoProtocol, selected_source: str | None, selected_dest: str | None) -> go.Figure:
    """The bipartite graph of create_summary.py. Every node is a point with customdata ['source'|'dest', barcode]."""
    sources, destinations = protocol.sources, protocol.destinations
    height = max(len(sources), len(destinations))

    def y_positions(plates: list[str]) -> dict[str, float]:
        # spread the plates evenly over the same height
        return {plate: height - (i + 0.5) * height / len(plates) for i, plate in enumerate(plates)}

    source_y, dest_y = y_positions(sources), y_positions(destinations)
    edges: dict[tuple[str, str], int] = {}
    for t in protocol.transfers:
        edges[(t.source, t.dest)] = edges.get((t.source, t.dest), 0) + 1

    fig = go.Figure()
    annotations = []
    for (source, dest), count in sorted(edges.items()):
        selected = source == selected_source and dest == selected_dest
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[source_y[source], dest_y[dest]], mode="lines", hoverinfo="skip",
            line={"color": SELECTED_BORDER if selected else EDGE_COLOR, "width": 3 if selected else 1},
        ))
        # the label sits closer to the source, so the labels of edges ending at the same plate do not overlap
        annotations.append({
            "x": 0.3, "y": 0.7 * source_y[source] + 0.3 * dest_y[dest], "text": str(count), "showarrow": False,
            "bgcolor": "white", "font": {"size": 11, "color": SELECTED_BORDER if selected else EDGE_COLOR},
        })

    for kind, plates, x, y, fill, selected in (
        ("source", sources, 0, source_y, SOURCE_FILL, selected_source),
        ("dest", destinations, 1, dest_y, DEST_FILL, selected_dest),
    ):
        totals = {plate: len(protocol.transfers_of(**{kind: plate})) for plate in plates}
        for plate in plates:
            annotations.append({
                "x": x, "y": y[plate], "showarrow": False, "text": f"<b>{plate}</b><br>{totals[plate]} transfers",
                "bgcolor": fill, "borderpad": 6, "borderwidth": 3 if plate == selected else 1,
                "bordercolor": SELECTED_BORDER if plate == selected else NODE_BORDER, "font": {"size": 12},
            })
        # invisible points below the boxes receive the clicks
        fig.add_trace(go.Scatter(
            x=[x] * len(plates), y=[y[plate] for plate in plates], mode="markers",
            marker={"size": 40, "opacity": 0}, customdata=[[kind, plate] for plate in plates],
            hovertemplate="%{customdata[1]}<extra>click to show</extra>",
        ))
    annotations += [
        {"x": 0, "y": height, "yshift": 10, "text": "<b>Sources</b>", "showarrow": False, "yanchor": "bottom"},
        {"x": 1, "y": height, "yshift": 10, "text": "<b>Destinations</b>", "showarrow": False, "yanchor": "bottom"},
    ]
    fig.update_layout(
        annotations=annotations, showlegend=False, hovermode="closest", hoverdistance=60, clickmode="event",
        height=max(300, 80 * height + 60), margin={"l": 70, "r": 70, "t": 30, "b": 10},
        xaxis={"visible": False, "range": [-0.25, 1.25], "fixedrange": True},
        yaxis={"visible": False, "range": [-0.1, height + 0.1], "fixedrange": True},
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig


def plate_view(title: str, rows: int, columns: int, wells: dict[str, tuple[str, str, str]]):
    """
    The plate layout with row letters and column numbers on all sides.
    :param wells: well -> (text, background color, tooltip) of all wells to highlight
    """
    cell = 34 if columns <= 12 else 21 if columns <= 24 else 13
    font = max(6, cell // 3)
    label_style = {"fontSize": f"{font + 1}px", "color": "#4a5568", "display": "flex", "alignItems": "center",
                   "justifyContent": "center"}

    def label(text, row: int, column: int):
        return html.Div(text, style={**label_style, "gridRow": row, "gridColumn": column})

    children = []
    for column in range(columns):
        children += [label(column + 1, 1, column + 2), label(column + 1, rows + 2, column + 2)]
    for row in range(rows):
        children += [label(row_name(row), row + 2, 1), label(row_name(row), row + 2, columns + 2)]
    for row in range(rows):
        for column in range(columns):
            well = f"{row_name(row)}{column + 1}"
            text, color, tooltip = wells.get(well, ("", "white", well))
            children.append(html.Div(text, title=tooltip, style={
                "gridRow": row + 2, "gridColumn": column + 2, "background": color, "border": "1px solid #a0aec0",
                "borderRadius": "50%" if columns <= 24 else "2px", "fontSize": f"{font}px", "overflow": "hidden",
                "display": "flex", "alignItems": "center", "justifyContent": "center", "lineHeight": 1,
            }))
    return html.Div([
        html.Div(title, style={"fontWeight": "bold", "marginBottom": "4px"}),
        html.Div(children, style={
            "display": "grid", "gap": "1px", "width": "max-content",
            "gridTemplateColumns": f"{cell}px repeat({columns}, {cell}px) {cell}px",
            "gridTemplateRows": f"{cell}px repeat({rows}, {cell}px) {cell}px",
        }),
    ])


def source_plate_view(protocol: EchoProtocol, source: str):
    colors = source_well_colors(protocol, source)
    transfers = protocol.transfers_of(source=source)
    wells = {}
    for well, color in colors.items():
        leaving = [t for t in transfers if t.source_well == well]
        tooltip = "\n".join([well] + [f"{format_volume(t.volume)} nL to {t.dest} {t.dest_well}" for t in leaving])
        wells[well] = (format_volume(sum(t.volume for t in leaving)), color, tooltip)
    rows, columns = plate_format(list(colors), protocol.plate_types.get(source, ""))
    total = format_volume(sum(t.volume for t in transfers))
    return plate_view(f"Source {source}: {len(transfers)} transfers, {total} nL from {len(colors)} wells",
                      rows, columns, wells)


def dest_plate_view(protocol: EchoProtocol, dest: str, selected_source: str | None):
    colors = source_well_colors(protocol, selected_source) if selected_source else {}
    transfers = protocol.transfers_of(dest=dest)
    wells = {}
    for well in {t.dest_well for t in transfers}:
        arriving = [t for t in transfers if t.dest_well == well]
        # the color of the (first) source well of the selected source plate, if any
        from_selected = [t for t in arriving if t.source == selected_source]
        color = colors[from_selected[0].source_well] if from_selected else OTHER_WELL_COLOR
        tooltip = "\n".join([well] + [f"{format_volume(t.volume)} nL from {t.source} {t.source_well}"
                                      for t in arriving])
        wells[well] = (format_volume(sum(t.volume for t in arriving)), color, tooltip)
    rows, columns = plate_format(list(wells), protocol.plate_types.get(dest, ""))
    title = f"Destination {dest}: {len(transfers)} transfers"
    if selected_source:
        title += f", {len([t for t in transfers if t.source == selected_source])} from {selected_source} (colored)"
    return plate_view(title, rows, columns, wells)


@dataclass
class PlateLocation:
    """Where a plate of the protocol is and where it goes"""
    role: str  # "source" or "destination"
    device: str  # current device (from the database or chosen)
    target: str  # device the plate is brought to at the end
    db_device: str | None = None  # current device according to the database (None if unknown)
    db_slot: int | None = None

    @property
    def position_from_db(self) -> bool:
        """whether the orchestrator takes the start position from the database (by barcode)"""
        return self.db_device is not None and self.device == self.db_device


def default_location(role: str, db_info: ContainerInfo | None) -> PlateLocation:
    """current device from the database if known, the default storage of the role otherwise. The target is the
    current device if plates can be brought there."""
    default = DEFAULT_DEVICES[role]
    if db_info is None or not db_info.current_device:
        return PlateLocation(role=role, device=default, target=default)
    device = db_info.current_device
    return PlateLocation(role=role, device=device, target=device if device in TARGET_DEVICES else default,
                         db_device=device, db_slot=db_info.current_pos)


def find_process_problems(protocol: EchoProtocol | None, locations: dict[str, PlateLocation]) -> list[str]:
    if protocol is None or not protocol.transfers:
        return ["Load a protocol first."]
    problems = []
    if protocol.errors:
        problems.append(f"Fix the problems in {PurePath(protocol.filename).name} first.")
    both = sorted(set(protocol.sources) & set(protocol.destinations))
    if both:
        problems.append(f"{', '.join(both)} are source and destination plate. That is not supported.")
    for plate in protocol.sources + protocol.destinations:
        location = locations.get(plate)
        if location is None or location.device not in DEVICE_ATTRIBUTES and not location.position_from_db:
            problems.append(f"Choose where {plate} is.")
        if location is None or location.target not in TARGET_DEVICES:
            problems.append(f"Choose where {plate} goes.")
    return problems


def create_process_source(name: str, protocol: EchoProtocol, locations: dict[str, PlateLocation],
                          start_slots: dict[str, int]) -> str:
    """
    Writes the pythonLab process: each source plate is surveyed in the Echo, then each destination plate receiving
    liquid from it comes in, gets its transfers and goes to its target. Finally, the source plate goes to its target.
    :param start_slots: plate -> start slot of all plates whose start position is not taken from the database
    """
    sources, destinations = protocol.sources, protocol.destinations
    plates = sources + destinations
    index = {plate: i for i, plate in enumerate(plates)}
    plate_types = [protocol.plate_types.get(plate, DEFAULT_PLATE_TYPES["source"]) for plate in sources] \
        + [protocol.plate_types.get(plate, DEFAULT_PLATE_TYPES["dest"]) for plate in destinations]
    class_name = re.sub(r"\W", "_", name)
    transfer_lines = "\n".join(
        f"    ({t.source!r}, {t.source_well!r}, {t.dest!r}, {t.dest_well!r}, {t.volume!r}),"
        for t in protocol.transfers)

    start_lines = []
    for plate, slot in start_slots.items():
        attribute = DEVICE_ATTRIBUTES[locations[plate].device]
        start_lines.append(f"        self.containers[{index[plate]}].set_start_position(self.{attribute}, {slot})"
                           f"  # {plate}")
    start_positions = ""
    if start_lines:
        start_positions = "\n        # plates whose start position is not taken from the database\n" \
                          + "\n".join(start_lines)

    def move(cont: str, plate: str, **kwargs) -> str:
        args = "".join(f", {key}={value!r}" for key, value in kwargs.items())
        return f"        self.robot_arm.move({cont}, self.{DEVICE_ATTRIBUTES[locations[plate].target]}{args})"

    steps = []
    dest_in_echo_before: set[str] = set()
    for source in sources:
        steps += [
            "",
            f"        # source plate {source}",
            f"        src = self.containers[{index[source]}]",
            # the first move of each plate assures its barcode (the step fails if another plate was picked)
            "        self.robot_arm.move(src, self.echo, role='source', assure_barcode=True, lidded=False)",
            f"        self.echo.survey_for_protocol(source_plate=src, protocol=transfers({source!r}))",
            "        src.wait_cost(20)",
        ]
        for dest in destinations:
            count = len(protocol.transfers_of(source=source, dest=dest))
            if not count:
                continue
            # the barcode of each destination plate is assured when it comes to the Echo the first time
            assure_barcode = ", assure_barcode=True" if dest not in dest_in_echo_before else ""
            dest_in_echo_before.add(dest)
            steps += [
                f"        # {source} -> {dest}: {count} transfers",
                f"        dest = self.containers[{index[dest]}]",
                f"        self.robot_arm.move(dest, self.echo, role='destination'{assure_barcode}, lidded=False)",
                f"        self.echo.execute_transfer_protocol(src, dest, transfers({source!r}, {dest!r}))",
                move("dest", dest, lidded=True),
                "        src.wait_cost(20)",
            ]
        steps.append(move("src", source, lidded=True))
    process_steps = "\n".join(steps)
    return f'''"""
Echo process created by the Echo plugin from {PurePath(protocol.filename).name}.
Each source plate is surveyed, then every destination plate receiving liquid from it gets its transfers.
All plates go to their target device afterwards.
"""

import pandas as pd
from pythonlab.resource import LabwareResource
from lab_adaption.processes.basic_process import BasicProcess

# (source plate, source well, destination plate, destination well, transfer volume in nL)
TRANSFERS = [
{transfer_lines}
]


def transfers(source, dest=None):
    """The transfers from the source plate (to the destination plate) in the format of the Echo steps"""
    rows = [t for t in TRANSFERS if t[0] == source and (dest is None or t[2] == dest)]
    return pd.DataFrame([(t[1], t[3], t[4]) for t in rows],
                        columns=["Source well", "Destination well", "Transfer Volume"])


class {class_name}(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates={len(plates)},
            process_name={name!r},
        )

    def create_resources(self):
        # only the devices come from BasicProcess, the plates are created here
        num_plates, self.num_mw_plates = self.num_mw_plates, 0
        super().create_resources()
        self.num_mw_plates = num_plates
        plate_types = {plate_types!r}
        # the orchestrator puts the process name in front: <process name>_plate<index>
        self.containers = [
            LabwareResource(proc=self, name=f"plate{{i}}", lidded=True, filled=False, plate_type=plate_types[i])
            for i in range(num_plates)
        ]

    def init_service_resources(self):
        super().init_service_resources()
        # sources: {sources!r}
        # destinations: {destinations!r}
        barcodes = {plates!r}
        for i, cont in enumerate(self.containers):
            cont.set_barcode(barcodes[i]){start_positions}

    def process(self):{process_steps}
'''


class EchoPlugin(PluginInterface):
    """
    The loaded protocol, the selected plates and the plate locations are kept here, so closing and reopening the
    pop-up window keeps them.
    """
    def __init__(self, orchestrator, process_module=None):
        super().__init__(orchestrator, process_module)
        self._protocol: EchoProtocol | None = None
        self._source: str | None = None
        self._dest: str | None = None
        self._locations: dict[str, PlateLocation] = {}  # plate barcode -> location

    def get_name(self) -> str:
        return "Echo"

    # ---------- state ----------

    def _load(self, filename: str, content: str):
        try:
            text = base64.b64decode(content.split(",", 1)[1]).decode("utf-8-sig")
        except Exception:
            self._protocol = EchoProtocol(filename=filename, errors=["The file could not be read as text."])
        else:
            self._protocol = parse_protocol(filename, text)
        self._source = self._dest = None
        self._read_locations()

    def _db_info(self, barcode: str) -> ContainerInfo | None:
        try:
            return self.orchestrator.db_client.get_cont_info_by_barcode(barcode)
        except Exception:
            Logger.warning(f"Echo plugin could not look up {barcode} in the database:\n{traceback.format_exc()}")
            return None

    def _read_locations(self):
        protocol = self._protocol
        self._locations = {}
        for role, plates in (("source", protocol.sources), ("destination", protocol.destinations)):
            for plate in plates:
                self._locations.setdefault(plate, default_location(role, self._db_info(plate)))

    def _select(self, click_data: dict):
        kind, plate = click_data["points"][0]["customdata"]
        if kind == "source":
            self._source = plate
        else:
            self._dest = plate

    def _free_slots(self, device: str) -> list[int] | None:
        """free slots of the device according to the database, None if the database does not know"""
        db = self.orchestrator.db_client
        # the dummy database (no database configured) knows nothing about the slots
        if isinstance(db, StatusDBDummyImplementation):
            return None
        try:
            positions = db.get_all_positions(device)
            if not positions:
                return None
            return [pos for pos in sorted(positions) if db.position_empty(device, pos)]
        except Exception:
            Logger.warning(f"Echo plugin could not read the free slots of {device}:\n{traceback.format_exc()}")
            return None

    def _start_slots(self) -> tuple[dict[str, int], list[str]]:
        """
        Start slots of the plates whose position is not taken from the database: the first free slots of their
        device according to the database or, if it does not know them, consecutive slots starting with 0.
        :return: plate -> slot and the problems
        """
        slots, problems = {}, []
        by_device: dict[str, list[str]] = {}
        for plate, location in self._locations.items():
            if not location.position_from_db:
                by_device.setdefault(location.device, []).append(plate)
        for device, plates in by_device.items():
            free = self._free_slots(device)
            if free is None:
                free = list(range(len(plates)))
            if len(free) < len(plates):
                problems.append(f"{device} has only {len(free)} free slot(s) for {', '.join(plates)}.")
                continue
            slots.update(zip(plates, free))
        return slots, problems

    def _process_name(self) -> str:
        """EchoProcess<number> with the lowest number not in use (the orchestrator would rename a taken name)"""
        taken = set(self.orchestrator.jssp.process_by_name)
        number = 1
        while f"{PROCESS_NAME_PREFIX}{number}" in taken:
            number += 1
        return f"{PROCESS_NAME_PREFIX}{number}"

    # ---------- plugin interface ----------

    def get_layout(self):
        return html.Div(className="echo-plugin", style={
            "display": "grid", "gridTemplateColumns": "minmax(0, auto) minmax(320px, 1fr)", "gap": "16px",
            "width": "min(1500px, 85vw)", "alignItems": "start",
        }, children=[
            html.Div(style={"display": "flex", "flexDirection": "column", "gap": "16px", "minWidth": 0}, children=[
                html.Div([
                    dcc.Upload(
                        id="echo_upload",
                        multiple=False,
                        accept=".csv,text/csv",
                        children=html.Div(["Drag and drop an Echo protocol csv file here or ", html.A("browse")]),
                        style={"border": "2px dashed #888", "borderRadius": "8px", "padding": "24px",
                               "textAlign": "center", "cursor": "pointer"},
                    ),
                    html.Div(id="echo_status", children=self._render_status(), style={"marginTop": "8px"}),
                ]),
                html.Div(id="echo_source_plate", children=self._render_source(), style={"overflowX": "auto"}),
                html.Div(id="echo_dest_plate", children=self._render_dest(), style={"overflowX": "auto"}),
            ]),
            html.Div([
                html.Div(self._render_graph()),
                html.Div(id="echo_targets", children=self._render_targets()),
                dcc.Store(id="echo_targets_store"),
            ]),
        ])

    def register_callbacks(self, app: DashProxy) -> None:
        @app.callback(
            Output("echo_status", "children"),
            Output("echo_graph", "figure"),
            Output("echo_graph", "style"),
            Output("echo_graph_hint", "style"),
            Output("echo_source_plate", "children"),
            Output("echo_dest_plate", "children"),
            Output("echo_targets", "children"),
            Output("echo_upload", "contents"),
            Input("echo_upload", "contents"),
            Input("echo_graph", "clickData"),
            State("echo_upload", "filename"),
            prevent_initial_call=True,
        )
        def update_content(contents, click_data, filename):
            triggered = callback_context.triggered[0]["prop_id"].split(".")[0] if callback_context.triggered else None
            try:
                if triggered == "echo_upload":
                    if not contents:
                        return (no_update,) * 8
                    self._load(filename, contents)
                    targets = self._render_targets()
                elif triggered == "echo_graph" and click_data and self._protocol is not None:
                    self._select(click_data)
                    # re-rendering the list would not change it
                    targets = no_update
                else:
                    return (no_update,) * 8
            except Exception:
                Logger.error(f"Echo plugin failed to handle {triggered}:\n{traceback.format_exc()}")
                targets = self._render_targets()
            graph_style, hint_style = self._graph_styles()
            # resetting the contents allows loading the same file again
            return (self._render_status(), self._figure(), graph_style, hint_style, self._render_source(),
                    self._render_dest(), targets, None)

        @app.callback(
            Output("echo_targets_store", "data"),
            Output({"type": "echo_position", "plate": ALL}, "children"),
            Input({"type": "echo_current", "plate": ALL}, "value"),
            Input({"type": "echo_target", "plate": ALL}, "value"),
            State({"type": "echo_current", "plate": ALL}, "id"),
            prevent_initial_call=True,
        )
        def choose_devices(currents, targets, ids):
            notes = []
            for current, target, id_ in zip(currents, targets, ids):
                location = self._locations.get(id_["plate"])
                if location is None:
                    notes.append(None)
                    continue
                location.device = current or location.device
                location.target = target or location.target
                notes.append(self._position_note(location))
            return {plate: (loc.device, loc.target) for plate, loc in self._locations.items()}, notes

    def add_process_clicked(self) -> str | None:
        problems = find_process_problems(self._protocol, self._locations)
        if problems:
            return " ".join(problems)
        start_slots, problems = self._start_slots()
        if problems:
            return " ".join(problems)
        name = self._process_name()
        try:
            source = create_process_source(name, self._protocol, self._locations, start_slots)
            self.orchestrator.add_process(description=source, name=name)
        except Exception as ex:
            Logger.warning(f"Echo plugin could not add the process {name}:\n{traceback.format_exc()}")
            return f"The process could not be added: {ex}"
        Logger.info(f"Echo plugin added the process {name} with {len(self._protocol.transfers)} transfers")
        return None

    # ---------- rendering ----------

    def _render_status(self):
        protocol = self._protocol
        if protocol is None:
            return "No protocol loaded."
        children = [html.Div(PurePath(protocol.filename).name + (
            f": {len(protocol.transfers)} transfers from {len(protocol.sources)} source plate(s) to "
            f"{len(protocol.destinations)} destination plate(s)" if protocol.transfers else ""))]
        children += [html.Div(error, style={"color": "#c62828"}) for error in protocol.errors[:10]]
        if len(protocol.errors) > 10:
            children.append(html.Div(f"... and {len(protocol.errors) - 10} more problems", style={"color": "#c62828"}))
        return children

    def _has_transfers(self) -> bool:
        return self._protocol is not None and bool(self._protocol.transfers)

    def _figure(self) -> go.Figure:
        if not self._has_transfers():
            return go.Figure()
        return create_graph(self._protocol, self._source, self._dest)

    def _graph_styles(self) -> tuple[dict, dict]:
        """styles of the graph and the hint shown instead of it"""
        hidden = {"display": "none"}
        if self._has_transfers():
            return {}, hidden
        return hidden, {"color": "#718096"}

    def _render_graph(self):
        # the graph always exists, so the callback can listen to its clicks
        graph_style, hint_style = self._graph_styles()
        return [
            html.Div("Load a protocol to see its plates and transfers.", id="echo_graph_hint", style=hint_style),
            dcc.Graph(id="echo_graph", figure=self._figure(), style=graph_style, config={"displayModeBar": False}),
        ]

    @staticmethod
    def _position_note(location: PlateLocation) -> str:
        if location.position_from_db:
            return f"slot {location.db_slot} (database)"
        if location.db_device is None:
            return "not in the database"
        return f"database: {location.db_device} {location.db_slot}"

    def _render_targets(self):
        if not self._has_transfers():
            return None
        rows = []
        for kind, plates, fill in (("source", self._protocol.sources, SOURCE_FILL),
                                   ("destination", self._protocol.destinations, DEST_FILL)):
            for plate in plates:
                location = self._locations[plate]
                # the device from the database is offered even if plates can not be brought there
                current_options = TARGET_DEVICES + ([location.db_device] if location.db_device
                                                    and location.db_device not in TARGET_DEVICES else [])
                rows.append(html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                    html.Span(plate, title=f"{kind} plate", style={
                        "background": fill, "border": f"1px solid {NODE_BORDER}", "borderRadius": "4px",
                        "padding": "2px 8px", "fontWeight": "bold", "minWidth": "110px", "textAlign": "center"}),
                    dcc.Dropdown(
                        id={"type": "echo_current", "plate": plate}, options=current_options,
                        value=location.device, clearable=False, style={"width": "140px"},
                    ),
                    html.Span(self._position_note(location), id={"type": "echo_position", "plate": plate},
                              style={"fontSize": "0.8em", "color": "#718096", "minWidth": "120px"}),
                    html.Span("→", style={"fontSize": "18px"}),
                    dcc.Dropdown(
                        id={"type": "echo_target", "plate": plate}, options=TARGET_DEVICES,
                        value=location.target, clearable=False, style={"width": "140px"},
                    ),
                ]))
        header_style = {"fontSize": "0.85em", "color": "#4a5568"}
        header = html.Div(style={"display": "flex", "gap": "10px"}, children=[
            html.Span("Plate", style={**header_style, "minWidth": "128px"}),
            html.Span("Current device", style={**header_style, "minWidth": "274px"}),
            html.Span("Target", style=header_style),
        ])
        return html.Div([html.H4("Plates", style={"margin": "12px 0 6px"}), header,
                         html.Div(rows, style={"display": "flex", "flexDirection": "column", "gap": "6px"})])

    def _render_source(self):
        if not self._has_transfers():
            return None
        if self._source is None:
            return html.Div("Click a source plate in the graph to see its layout.", style={"color": "#718096"})
        return source_plate_view(self._protocol, self._source)

    def _render_dest(self):
        if not self._has_transfers():
            return None
        if self._dest is None:
            return html.Div("Click a destination plate in the graph to see its layout.", style={"color": "#718096"})
        return dest_plate_view(self._protocol, self._dest, self._source)

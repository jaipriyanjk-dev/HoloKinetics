import cv2
import mediapipe as mp
import math
import time

# ============================================================
# JARVIS HOLOGRAPHIC ATOM CONTROL
# Iron Man inspired interactive atomic manipulation system
# ============================================================

# ---------------- CAMERA ----------------

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

try:
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except:
    pass


# ---------------- MEDIAPIPE ----------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.72,
    min_tracking_confidence=0.72
)


# ============================================================
# COLORS - BGR
# ============================================================

CYAN = (255, 255, 0)
BRIGHT_CYAN = (255, 255, 120)
DARK_CYAN = (160, 170, 0)

WHITE = (255, 255, 255)
SOFT_WHITE = (210, 230, 230)

RED = (60, 70, 255)
BRIGHT_RED = (80, 100, 255)

BLUE = (255, 180, 50)
GREEN = (100, 255, 130)

YELLOW = (0, 255, 255)
PURPLE = (220, 100, 255)


# ============================================================
# ATOM POSITION / SIZE
# ============================================================

atom_x = 320.0
atom_y = 240.0

atom_scale = 0.48

MIN_SCALE = 0.08
MAX_SCALE = 0.85


# ============================================================
# 3D ROTATION
# ============================================================

rotation_x = 0.0
rotation_y = 0.0
rotation_z = 0.0


# ============================================================
# NUCLEUS PARTICLES
#
# Coordinates are normalized 3D coordinates.
# ============================================================

particles = [

    # ---------- PROTONS ----------

    {
        "type": "PROTON",
        "x": -0.25,
        "y": -0.15,
        "z": 0.10
    },

    {
        "type": "PROTON",
        "x": 0.15,
        "y": -0.25,
        "z": 0.05
    },

    {
        "type": "PROTON",
        "x": 0.30,
        "y": 0.05,
        "z": 0.00
    },

    {
        "type": "PROTON",
        "x": -0.10,
        "y": 0.20,
        "z": -0.05
    },

    {
        "type": "PROTON",
        "x": 0.10,
        "y": 0.25,
        "z": -0.15
    },

    {
        "type": "PROTON",
        "x": -0.30,
        "y": 0.10,
        "z": 0.15
    },

    {
        "type": "PROTON",
        "x": 0.00,
        "y": -0.05,
        "z": 0.22
    },

    # ---------- NEUTRONS ----------

    {
        "type": "NEUTRON",
        "x": 0.00,
        "y": 0.00,
        "z": 0.00
    },

    {
        "type": "NEUTRON",
        "x": -0.18,
        "y": -0.05,
        "z": -0.20
    },

    {
        "type": "NEUTRON",
        "x": 0.18,
        "y": -0.05,
        "z": -0.20
    },

    {
        "type": "NEUTRON",
        "x": -0.05,
        "y": 0.25,
        "z": 0.20
    },

    {
        "type": "NEUTRON",
        "x": 0.05,
        "y": -0.25,
        "z": 0.00
    },

    {
        "type": "NEUTRON",
        "x": -0.20,
        "y": 0.05,
        "z": 0.00
    },

    {
        "type": "NEUTRON",
        "x": 0.20,
        "y": 0.15,
        "z": 0.12
    }
]


# ============================================================
# ELECTRONS
# ============================================================

electrons = [

    {
        "radius": 0.72,
        "angle": 0.0,
        "speed": 0.030,
        "plane": 0
    },

    {
        "radius": 0.90,
        "angle": 1.8,
        "speed": -0.022,
        "plane": 1
    },

    {
        "radius": 1.05,
        "angle": 3.5,
        "speed": 0.018,
        "plane": 2
    },

    {
        "radius": 1.18,
        "angle": 5.0,
        "speed": -0.015,
        "plane": 0
    },

    {
        "radius": 0.82,
        "angle": 4.2,
        "speed": 0.025,
        "plane": 1
    },

    {
        "radius": 1.28,
        "angle": 2.4,
        "speed": -0.012,
        "plane": 2
    }
]


# ============================================================
# INTERACTION STATE
# ============================================================

selected_type = None
selected_index = None

particle_dragging = False

grab_offset_x = 0.0
grab_offset_y = 0.0

hand_data = []

smooth_hands = {}

previous_hand_distance = None
previous_hand_angle = None

previous_center_x = None
previous_center_y = None


# ============================================================
# VISUAL EFFECT STATE
# ============================================================

scan_angle = 0.0
pulse = 0.0

last_time = time.time()


# ============================================================
# BASIC FUNCTIONS
# ============================================================

def distance(x1, y1, x2, y2):
    return math.hypot(
        x2 - x1,
        y2 - y1
    )


def smooth(old, new, amount):
    return old + (new - old) * amount


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(maximum, value)
    )


def angle_difference(target, current):
    return (target - current + 180) % 360 - 180


# ============================================================
# 3D ROTATION
# ============================================================

def rotate_3d(x, y, z):

    # X rotation
    rx = math.radians(rotation_x)

    y1 = (
        y * math.cos(rx)
        -
        z * math.sin(rx)
    )

    z1 = (
        y * math.sin(rx)
        +
        z * math.cos(rx)
    )

    # Y rotation
    ry = math.radians(rotation_y)

    x2 = (
        x * math.cos(ry)
        +
        z1 * math.sin(ry)
    )

    z2 = (
        -x * math.sin(ry)
        +
        z1 * math.cos(ry)
    )

    # Z rotation
    rz = math.radians(rotation_z)

    x3 = (
        x2 * math.cos(rz)
        -
        y1 * math.sin(rz)
    )

    y3 = (
        x2 * math.sin(rz)
        +
        y1 * math.cos(rz)
    )

    return x3, y3, z2


# ============================================================
# 3D PROJECTION
# ============================================================

def project_3d(x, y, z):

    depth = 2.8

    factor = depth / (
        depth + z
    )

    px = (
        atom_x
        +
        x * 190
        * atom_scale
        * factor
    )

    py = (
        atom_y
        +
        y * 190
        * atom_scale
        * factor
    )

    return int(px), int(py), factor


# ============================================================
# PARTICLE POSITION
# ============================================================

def particle_screen_position(particle):

    x, y, z = rotate_3d(
        particle["x"],
        particle["y"],
        particle["z"]
    )

    return project_3d(
        x,
        y,
        z
    )


# ============================================================
# ELECTRON POSITION
# ============================================================

def electron_3d_position(electron):

    radius = electron["radius"]

    angle = electron["angle"]

    x = radius * math.cos(angle)

    y = radius * math.sin(angle)

    z = 0.0

    # Different orbital planes

    if electron["plane"] == 1:

        z = (
            0.22
            *
            math.sin(angle)
        )

    elif electron["plane"] == 2:

        original_x = x

        x = original_x * 0.65

        z = (
            radius
            *
            math.sin(angle)
            *
            0.45
        )

    return x, y, z


def electron_screen_position(electron):

    x, y, z = electron_3d_position(
        electron
    )

    x, y, z = rotate_3d(
        x,
        y,
        z
    )

    return project_3d(
        x,
        y,
        z
    )


# ============================================================
# HOLOGRAPHIC GLOW
# ============================================================

def glow_circle(
    frame,
    center,
    radius,
    color,
    strength=2
):

    overlay = frame.copy()

    for i in range(strength, 0, -1):

        r = radius + i * 4

        alpha = 0.04

        cv2.circle(
            overlay,
            center,
            r,
            color,
            1,
            cv2.LINE_AA
        )

    cv2.addWeighted(
        overlay,
        0.35,
        frame,
        0.65,
        0,
        frame
    )


# ============================================================
# ORBITAL RING
# ============================================================

def draw_orbit(
    frame,
    radius,
    axis
):

    points = []

    for i in range(140):

        angle = (
            2
            *
            math.pi
            *
            i
            /
            140
        )

        x = radius * math.cos(angle)

        y = radius * math.sin(angle)

        z = 0

        if axis == 0:

            y, z = z, y

        elif axis == 1:

            x, z = z, x

        x, y, z = rotate_3d(
            x,
            y,
            z
        )

        px, py, factor = project_3d(
            x,
            y,
            z
        )

        points.append(
            (
                px,
                py,
                factor
            )
        )

    for i in range(
        len(points) - 1
    ):

        p1 = points[i]

        p2 = points[i + 1]

        intensity = int(
            clamp(
                p1[2] * 100,
                20,
                100
            )
        )

        color = (
            intensity,
            intensity,
            0
        )

        cv2.line(
            frame,
            (p1[0], p1[1]),
            (p2[0], p2[1]),
            color,
            1,
            cv2.LINE_AA
        )


# ============================================================
# NUCLEUS RING
# ============================================================

def draw_nucleus(frame):

    radius = max(
        3,
        int(
            58
            *
            atom_scale
        )
    )

    center = (
        int(atom_x),
        int(atom_y)
    )

    cv2.circle(
        frame,
        center,
        radius + 7,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        center,
        radius,
        CYAN,
        1,
        cv2.LINE_AA
    )


# ============================================================
# PARTICLE DRAW
# ============================================================

def draw_particle(
    frame,
    particle,
    index
):

    px, py, factor = (
        particle_screen_position(
            particle
        )
    )

    base_radius = max(
        4,
        int(
            10
            *
            factor
            *
            atom_scale
            +
            2
        )
    )

    if particle["type"] == "PROTON":

        color = RED

    else:

        color = WHITE

    # Selection effect

    if (
        selected_type
        ==
        "PARTICLE"
        and
        selected_index
        ==
        index
    ):

        cv2.circle(
            frame,
            (px, py),
            base_radius + 15,
            DARK_CYAN,
            1,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            (px, py),
            base_radius + 10,
            CYAN,
            2,
            cv2.LINE_AA
        )

        # Four targeting corners

        corner = base_radius + 18

        cv2.line(
            frame,
            (px - corner, py - corner),
            (px - corner + 7, py - corner),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px + corner, py - corner),
            (px + corner - 7, py - corner),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px - corner, py + corner),
            (px - corner + 7, py + corner),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px + corner, py + corner),
            (px + corner - 7, py + corner),
            CYAN,
            1
        )

    glow_circle(
        frame,
        (px, py),
        base_radius,
        color,
        2
    )

    cv2.circle(
        frame,
        (px, py),
        base_radius,
        color,
        -1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        (px, py),
        max(2, base_radius // 3),
        CYAN,
        -1,
        cv2.LINE_AA
    )


# ============================================================
# ELECTRON DRAW
# ============================================================

def draw_electron(
    frame,
    electron,
    index
):

    px, py, factor = (
        electron_screen_position(
            electron
        )
    )

    size = max(
        4,
        int(
            6
            *
            factor
            *
            atom_scale
            +
            3
        )
    )

    # Electron trail

    for trail in range(1, 5):

        trail_angle = (
            electron["angle"]
            -
            electron["speed"]
            *
            trail
            *
            7
        )

        temp = electron.copy()

        temp["angle"] = trail_angle

        tx, ty, tf = (
            electron_screen_position(
                temp
            )
        )

        trail_size = max(
            1,
            size - trail
        )

        cv2.circle(
            frame,
            (tx, ty),
            trail_size,
            DARK_CYAN,
            1,
            cv2.LINE_AA
        )

    # Selected electron

    if (
        selected_type
        ==
        "ELECTRON"
        and
        selected_index
        ==
        index
    ):

        cv2.circle(
            frame,
            (px, py),
            size + 15,
            DARK_CYAN,
            1,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            (px, py),
            size + 10,
            CYAN,
            2,
            cv2.LINE_AA
        )

        cv2.line(
            frame,
            (px - 20, py),
            (px - 7, py),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px + 7, py),
            (px + 20, py),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px, py - 20),
            (px, py - 7),
            CYAN,
            1
        )

        cv2.line(
            frame,
            (px, py + 7),
            (px, py + 20),
            CYAN,
            1
        )

    glow_circle(
        frame,
        (px, py),
        size,
        CYAN,
        2
    )

    cv2.circle(
        frame,
        (px, py),
        size,
        BLUE,
        -1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        (px, py),
        max(2, size // 2),
        BRIGHT_CYAN,
        -1,
        cv2.LINE_AA
    )


# ============================================================
# ATOM
# ============================================================

def draw_atom(frame):

    # Back orbital rings

    draw_orbit(
        frame,
        0.70,
        0
    )

    draw_orbit(
        frame,
        0.90,
        1
    )

    draw_orbit(
        frame,
        1.10,
        2
    )

    # Outer orbital

    draw_orbit(
        frame,
        1.28,
        0
    )

    draw_nucleus(
        frame
    )

    # Particles

    for index, particle in enumerate(
        particles
    ):

        draw_particle(
            frame,
            particle,
            index
        )

    # Electrons

    for index, electron in enumerate(
        electrons
    ):

        draw_electron(
            frame,
            electron,
            index
        )


# ============================================================
# ACCURATE TARGET DETECTION
# ============================================================

def find_target(
    cursor_x,
    cursor_y
):

    closest_type = None

    closest_index = None

    closest_distance = float(
        "inf"
    )

    # ---------------- PARTICLES ----------------

    for index, particle in enumerate(
        particles
    ):

        px, py, factor = (
            particle_screen_position(
                particle
            )
        )

        d = distance(
            cursor_x,
            cursor_y,
            px,
            py
        )

        # Very controlled hit box

        selection_radius = max(
            8,
            int(
                12
                *
                factor
                *
                atom_scale
                +
                3
            )
        )

        if (
            d <= selection_radius
            and
            d < closest_distance
        ):

            closest_distance = d

            closest_type = "PARTICLE"

            closest_index = index

    # ---------------- ELECTRONS ----------------

    for index, electron in enumerate(
        electrons
    ):

        px, py, factor = (
            electron_screen_position(
                electron
            )
        )

        d = distance(
            cursor_x,
            cursor_y,
            px,
            py
        )

        selection_radius = max(
            7,
            int(
                11
                *
                factor
                *
                atom_scale
                +
                3
            )
        )

        if (
            d <= selection_radius
            and
            d < closest_distance
        ):

            closest_distance = d

            closest_type = "ELECTRON"

            closest_index = index

    return (
        closest_type,
        closest_index
    )


# ============================================================
# MOVE PARTICLE - HIGH ACCURACY
# ============================================================

def move_selected_particle(
    cursor_x,
    cursor_y
):

    if (
        selected_type
        !=
        "PARTICLE"
        or
        selected_index
        is None
    ):

        return

    particle = particles[
        selected_index
    ]

    scale = max(
        atom_scale,
        MIN_SCALE
    )

    # Convert screen position
    # back into atom space.

    target_x = (
        cursor_x
        -
        atom_x
    ) / (
        190
        *
        scale
    )

    target_y = (
        cursor_y
        -
        atom_y
    ) / (
        190
        *
        scale
    )

    # High precision following

    particle["x"] = smooth(
        particle["x"],
        target_x,
        0.88
    )

    particle["y"] = smooth(
        particle["y"],
        target_y,
        0.88
    )

    # Keep particle inside
    # reasonable nucleus area.

    particle["x"] = clamp(
        particle["x"],
        -0.62,
        0.62
    )

    particle["y"] = clamp(
        particle["y"],
        -0.62,
        0.62
    )


# ============================================================
# MOVE ELECTRON - HIGH ACCURACY
# ============================================================

def move_selected_electron(
    cursor_x,
    cursor_y
):

    if (
        selected_type
        !=
        "ELECTRON"
        or
        selected_index
        is None
    ):

        return

    electron = electrons[
        selected_index
    ]

    scale = max(
        atom_scale,
        MIN_SCALE
    )

    dx = (
        cursor_x
        -
        atom_x
    ) / (
        190
        *
        scale
    )

    dy = (
        cursor_y
        -
        atom_y
    ) / (
        190
        *
        scale
    )

    target_radius = math.sqrt(
        dx * dx +
        dy * dy
    )

    target_angle = math.atan2(
        dy,
        dx
    )

    # Much more responsive

    electron["radius"] = smooth(
        electron["radius"],
        target_radius,
        0.88
    )

    current_angle = (
        electron["angle"]
    )

    delta = angle_difference(
        target_angle,
        current_angle
    )

    electron["angle"] = (
        current_angle
        +
        delta * 0.88
    )

    # Controlled orbital range

    electron["radius"] = clamp(
        electron["radius"],
        0.42,
        1.45
    )


# ============================================================
# TWO HAND 3D CONTROL
# ============================================================

def process_two_hands():

    global atom_x
    global atom_y
    global atom_scale

    global rotation_x
    global rotation_y
    global rotation_z

    global previous_hand_distance
    global previous_hand_angle

    global previous_center_x
    global previous_center_y

    if len(hand_data) != 2:

        previous_hand_distance = None
        previous_hand_angle = None

        previous_center_x = None
        previous_center_y = None

        if len(hand_data) == 1:

            return "ONE HAND"

        return "READY"

    left = hand_data[0]

    right = hand_data[1]

    lx = left["x"]
    ly = left["y"]

    rx = right["x"]
    ry = right["y"]

    center_x = (
        lx + rx
    ) / 2

    center_y = (
        ly + ry
    ) / 2

    current_distance = distance(
        lx,
        ly,
        rx,
        ry
    )

    current_angle = math.degrees(
        math.atan2(
            ry - ly,
            rx - lx
        )
    )

    # Initialize

    if (
        previous_hand_distance
        is None
    ):

        previous_hand_distance = (
            current_distance
        )

        previous_hand_angle = (
            current_angle
        )

        previous_center_x = (
            center_x
        )

        previous_center_y = (
            center_y
        )

        return "TWO HANDS"

    # ---------------- SCALE ----------------

    distance_change = (
        current_distance
        -
        previous_hand_distance
    )

    atom_scale += (
        distance_change
        *
        0.0045
    )

    atom_scale = clamp(
        atom_scale,
        MIN_SCALE,
        MAX_SCALE
    )

    # ---------------- MOVE ----------------

    move_x = (
        center_x
        -
        previous_center_x
    )

    move_y = (
        center_y
        -
        previous_center_y
    )

    atom_x += (
        move_x
        *
        0.78
    )

    atom_y += (
        move_y
        *
        0.78
    )

    atom_x = clamp(
        atom_x,
        60,
        580
    )

    atom_y = clamp(
        atom_y,
        60,
        420
    )

    # ---------------- Z ROTATION ----------------

    angle_change = angle_difference(
        current_angle,
        previous_hand_angle
    )

    rotation_z += (
        angle_change
        *
        0.9
    )

    # ---------------- X/Y ROTATION ----------------

    rotation_x += (
        move_y
        *
        0.38
    )

    rotation_y += (
        move_x
        *
        0.38
    )

    rotation_x %= 360
    rotation_y %= 360
    rotation_z %= 360

    previous_hand_distance = (
        current_distance
    )

    previous_hand_angle = (
        current_angle
    )

    previous_center_x = (
        center_x
    )

    previous_center_y = (
        center_y
    )

    return "3D CONTROL"


# ============================================================
# HAND CURSOR
# ============================================================

def draw_cursor(
    frame,
    x,
    y,
    label
):

    x = int(x)
    y = int(y)

    # Outer targeting ring

    cv2.circle(
        frame,
        (x, y),
        14,
        CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        (x, y),
        4,
        CYAN,
        1,
        cv2.LINE_AA
    )

    # Crosshair

    cv2.line(
        frame,
        (x - 25, y),
        (x - 7, y),
        CYAN,
        1
    )

    cv2.line(
        frame,
        (x + 7, y),
        (x + 25, y),
        CYAN,
        1
    )

    cv2.line(
        frame,
        (x, y - 25),
        (x, y - 7),
        CYAN,
        1
    )

    cv2.line(
        frame,
        (x, y + 7),
        (x, y + 25),
        CYAN,
        1
    )

    cv2.putText(
        frame,
        label,
        (x + 20, y - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        CYAN,
        1,
        cv2.LINE_AA
    )


# ============================================================
# HOLOGRAPHIC GRID
# ============================================================

def draw_grid(frame):

    height, width = (
        frame.shape[:2]
    )

    # Perspective horizontal lines

    for y in range(
        80,
        height - 60,
        45
    ):

        cv2.line(
            frame,
            (0, y),
            (width, y),
            (30, 70, 70),
            1
        )

    # Vertical lines

    for x in range(
        20,
        width,
        60
    ):

        cv2.line(
            frame,
            (x, 60),
            (x, height - 60),
            (25, 60, 60),
            1
        )


# ============================================================
# SCANNING RING
# ============================================================

def draw_scan_effect(frame):

    global scan_angle

    scan_angle += 1.5

    radius = int(
        75
        *
        atom_scale
    )

    angle = math.radians(
        scan_angle
    )

    x = int(
        atom_x
        +
        radius
        *
        math.cos(angle)
    )

    y = int(
        atom_y
        +
        radius
        *
        math.sin(angle)
    )

    cv2.line(
        frame,
        (
            int(atom_x),
            int(atom_y)
        ),
        (x, y),
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )


# ============================================================
# HUD
# ============================================================

def draw_hud(
    frame,
    state
):

    height, width = (
        frame.shape[:2]
    )

    # Main title

    cv2.putText(
        frame,
        "JARVIS // HOLOGRAPHIC CONTROL",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "ATOMIC MANIPULATION SYSTEM",
        (20, 51),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )

    # ---------------- RIGHT PANEL ----------------

    panel_x = width - 210

    cv2.rectangle(
        frame,
        (panel_x, 18),
        (width - 18, 205),
        CYAN,
        1
    )

    cv2.putText(
        frame,
        "OBJECT",
        (panel_x + 12, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        DARK_CYAN,
        1
    )

    cv2.putText(
        frame,
        "ATOM",
        (panel_x + 105, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        WHITE,
        1
    )

    cv2.putText(
        frame,
        "STATE",
        (panel_x + 12, 67),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        DARK_CYAN,
        1
    )

    cv2.putText(
        frame,
        state,
        (panel_x + 90, 67),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        GREEN,
        1
    )

    cv2.putText(
        frame,
        f"SCALE {atom_scale:.2f}",
        (panel_x + 12, 94),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        WHITE,
        1
    )

    cv2.putText(
        frame,
        f"RX {int(rotation_x):03d}",
        (panel_x + 12, 118),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        WHITE,
        1
    )

    cv2.putText(
        frame,
        f"RY {int(rotation_y):03d}",
        (panel_x + 100, 118),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        WHITE,
        1
    )

    cv2.putText(
        frame,
        f"RZ {int(rotation_z):03d}",
        (panel_x + 12, 141),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        WHITE,
        1
    )

    # Target

    if selected_type == "PARTICLE":

        target = particles[
            selected_index
        ]["type"]

    elif selected_type == "ELECTRON":

        target = "ELECTRON"

    else:

        target = "NONE"

    cv2.putText(
        frame,
        "TARGET",
        (panel_x + 12, 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        DARK_CYAN,
        1
    )

    cv2.putText(
        frame,
        target,
        (panel_x + 92, 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        CYAN,
        1
    )

    # System status

    cv2.putText(
        frame,
        "● SYSTEM ONLINE",
        (panel_x + 12, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        GREEN,
        1
    )

    # ---------------- BOTTOM ----------------

    cv2.putText(
        frame,
        "TWO HANDS  MOVE / SCALE / ROTATE",
        (20, height - 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "PINCH  GRAB PROTON / NEUTRON / ELECTRON",
        (20, height - 39),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "CLOSE HANDS  MINIMIZE",
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Q : EXIT",
        (width - 70, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.32,
        DARK_CYAN,
        1,
        cv2.LINE_AA
    )


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:

        print(
            "Could not access camera"
        )

        break

    # Mirror camera

    frame = cv2.flip(
        frame,
        1
    )

    height, width = (
        frame.shape[:2]
    )

    # ---------------- BACKGROUND ----------------

    # Slight darkening for hologram effect

    frame = cv2.convertScaleAbs(
        frame,
        alpha=0.72,
        beta=-10
    )

    # Grid

    draw_grid(
        frame
    )

    # ---------------- MEDIAPIPE ----------------

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(
        rgb
    )

    hand_data = []

    # ---------------- HANDS ----------------

    if results.multi_hand_landmarks:

        for hand_index, hand in enumerate(
            results.multi_hand_landmarks
        ):

            index_tip = (
                hand.landmark[8]
            )

            thumb_tip = (
                hand.landmark[4]
            )

            wrist = (
                hand.landmark[0]
            )

            # Raw screen position

            raw_x = (
                index_tip.x
                *
                width
            )

            raw_y = (
                index_tip.y
                *
                height
            )

            # Smooth cursor

            if hand_index not in smooth_hands:

                smooth_hands[
                    hand_index
                ] = {
                    "x": raw_x,
                    "y": raw_y
                }

            else:

                smooth_hands[
                    hand_index
                ]["x"] = smooth(
                    smooth_hands[
                        hand_index
                    ]["x"],
                    raw_x,
                    0.55
                )

                smooth_hands[
                    hand_index
                ]["y"] = smooth(
                    smooth_hands[
                        hand_index
                    ]["y"],
                    raw_y,
                    0.55
                )

            x = smooth_hands[
                hand_index
            ]["x"]

            y = smooth_hands[
                hand_index
            ]["y"]

            # Thumb

            thumb_x = (
                thumb_tip.x
                *
                width
            )

            thumb_y = (
                thumb_tip.y
                *
                height
            )

            pinch_distance = distance(
                x,
                y,
                thumb_x,
                thumb_y
            )

            # Hand size reference

            hand_scale = distance(
                wrist.x * width,
                wrist.y * height,
                hand.landmark[9].x * width,
                hand.landmark[9].y * height
            )

            # Dynamic pinch threshold

            pinch_threshold = clamp(
                hand_scale * 0.34,
                18,
                48
            )

            pinch = (
                pinch_distance
                <
                pinch_threshold
            )

            hand_data.append(
                {
                    "x": x,
                    "y": y,
                    "pinch": pinch
                }
            )

            # Draw subtle hand skeleton

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(
                    color=DARK_CYAN,
                    thickness=1,
                    circle_radius=1
                ),
                mp_draw.DrawingSpec(
                    color=(80, 110, 110),
                    thickness=1
                )
            )

    # ========================================================
    # TWO HAND SYSTEM
    # ========================================================

    state = process_two_hands()

    # ========================================================
    # ONE HAND PARTICLE CONTROL
    # ========================================================

    if len(hand_data) >= 1:

        hand = hand_data[0]

        cursor_x = hand["x"]
        cursor_y = hand["y"]

        pinch = hand["pinch"]

        # Don't allow accidental
        # selection while two-hand
        # manipulation is active.

        if len(hand_data) == 1:

            target_type, target_index = (
                find_target(
                    cursor_x,
                    cursor_y
                )
            )

            # ---------------- GRAB ----------------

            if pinch:

                if (
                    not particle_dragging
                    and
                    target_type is not None
                ):

                    selected_type = (
                        target_type
                    )

                    selected_index = (
                        target_index
                    )

                    particle_dragging = True

            # ---------------- MOVE ----------------

            if (
                particle_dragging
                and
                pinch
            ):

                if (
                    selected_type
                    ==
                    "PARTICLE"
                ):

                    move_selected_particle(
                        cursor_x,
                        cursor_y
                    )

                elif (
                    selected_type
                    ==
                    "ELECTRON"
                ):

                    move_selected_electron(
                        cursor_x,
                        cursor_y
                    )

            # ---------------- RELEASE ----------------

            if (
                particle_dragging
                and
                not pinch
            ):

                particle_dragging = False

                selected_type = None

                selected_index = None

            # ---------------- CURSOR ----------------

            if particle_dragging:

                cursor_label = "LOCKED"

            elif (
                target_type
                ==
                "ELECTRON"
            ):

                cursor_label = "ELECTRON"

            elif (
                target_type
                ==
                "PARTICLE"
            ):

                cursor_label = "TARGET"

            else:

                cursor_label = "TRACK"

            draw_cursor(
                frame,
                cursor_x,
                cursor_y,
                cursor_label
            )

    # ========================================================
    # ELECTRON ANIMATION
    # ========================================================

    if not (
        particle_dragging
        and
        selected_type
        ==
        "ELECTRON"
    ):

        for electron in electrons:

            electron["angle"] += (
                electron["speed"]
            )

    # ========================================================
    # SCAN EFFECT
    # ========================================================

    draw_scan_effect(
        frame
    )

    # ========================================================
    # ATOM
    # ========================================================

    draw_atom(
        frame
    )

    # ========================================================
    # HUD
    # ========================================================

    draw_hud(
        frame,
        state
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "JARVIS Holographic Interface",
        frame
    )

    key = cv2.waitKey(
        1
    ) & 0xFF

    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

hands.close()

cv2.destroyAllWindows()
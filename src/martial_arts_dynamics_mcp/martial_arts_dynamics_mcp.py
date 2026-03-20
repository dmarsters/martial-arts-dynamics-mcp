"""
Martial Arts Dynamics MCP Server
=================================

Phase 2.6 + Phase 2.7 | Dal Marsters / Lushy Project

Translates the visual geometry of judo and jiu jitsu into compositional
parameters for image generation. Based on the insight that these two arts
represent complementary geometric systems:

- Judo: big circle, large arcs, vertical throws, explosive bursts
- Jiu Jitsu: small circle, tight spirals, ground compression, sustained pressure

The domain maps techniques and positions to a 5D parameter space that captures
the visual dynamics of bodies, gravity, and empty space in continuous cycles.

Phase 2.6 enhancements:
  Rhythmic presets with forced-orbit integration — guaranteed periodic closure,
  zero numerical drift. Presets model natural martial arts limit cycles:
  randori pulse (24), ground flow (20), art spectrum (30), compression
  release (16), vertical collapse (14).

Phase 2.7 enhancements:
  Attractor visualization prompt generation — translates morphospace coordinates
  into image-generation-ready prompts via nearest-neighbor visual vocabulary
  matching. Supports composite, sequence, and split-view modes.

Three-layer architecture:
  Layer 1: Pure taxonomy lookup (0 tokens)
  Layer 2: Deterministic NumPy computation (0 tokens)
  Layer 3: Creative synthesis (reserved for LLM caller)
"""

import json
import math
import numpy as np
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from fastmcp import FastMCP

mcp = FastMCP("martial_arts_dynamics_mcp")

# =============================================================================
# CONSTANTS: 5D Parameter Space
# =============================================================================

PARAMETER_NAMES = [
    "arc_radius",           # 0=tight spiral (BJJ) → 1=full body arc (judo)
    "vertical_displacement", # 0=ground plane → 1=aerial/standing
    "negative_space_ratio",  # 0=interlocked bodies → 1=explosive separation
    "kinetic_tempo",         # 0=sustained grinding → 1=explosive burst
    "gravitational_anchor",  # 0=low/rooted/stable → 1=elevated/unstable
]

# =============================================================================
# VISUAL TYPES: Regions of the 5D parameter space with image-gen keywords
# =============================================================================

VISUAL_TYPES = {
    "orbital_throw": {
        "coordinates": {
            "arc_radius": 0.9,
            "vertical_displacement": 0.85,
            "negative_space_ratio": 0.8,
            "kinetic_tempo": 0.9,
            "gravitational_anchor": 0.85,
        },
        "keywords": [
            "sweeping circular arc of two bodies rotating through vertical axis",
            "explosive rotational momentum with centrifugal separation",
            "large spiral trajectory against open negative space",
            "dynamic figure tracing parabolic flight path",
            "radial force vectors emanating from hip fulcrum point",
            "bodies describing planetary orbit with gravitational collapse",
            "peak kinetic energy at apex of circular throw arc",
        ],
    },
    "spiral_compression": {
        "coordinates": {
            "arc_radius": 0.15,
            "vertical_displacement": 0.1,
            "negative_space_ratio": 0.1,
            "kinetic_tempo": 0.2,
            "gravitational_anchor": 0.05,
        },
        "keywords": [
            "tightly wound limb spirals creating compact topology",
            "bodies interlocked in minimal negative space on ground plane",
            "sustained isometric pressure through compressed joint geometry",
            "small-radius curves of wrapped limbs and torsos",
            "dense figure-ground entanglement with no separation",
            "slow grinding rotational force through constricting coils",
            "gravitationally anchored mass pressed into mat surface",
        ],
    },
    "transition_flow": {
        "coordinates": {
            "arc_radius": 0.5,
            "vertical_displacement": 0.45,
            "negative_space_ratio": 0.5,
            "kinetic_tempo": 0.55,
            "gravitational_anchor": 0.5,
        },
        "keywords": [
            "mid-transition between standing exchange and ground engagement",
            "balanced interplay of open space and body contact",
            "fluid weight transfer through shifting center of gravity",
            "moderate arc curvature connecting vertical and horizontal planes",
            "rhythmic oscillation between expansion and compression",
            "limbs tracing medium spirals through transitional postures",
        ],
    },
    "impact_moment": {
        "coordinates": {
            "arc_radius": 0.7,
            "vertical_displacement": 0.95,
            "negative_space_ratio": 0.85,
            "kinetic_tempo": 1.0,
            "gravitational_anchor": 0.95,
        },
        "keywords": [
            "peak force instant frozen at maximum vertical displacement",
            "explosive separation of bodies at throw completion",
            "gravitational free-fall with full negative space exposure",
            "maximum kinetic burst at point of no return",
            "angular momentum releasing into ballistic trajectory",
            "shockwave composition radiating from impact origin",
        ],
    },
    "guard_architecture": {
        "coordinates": {
            "arc_radius": 0.25,
            "vertical_displacement": 0.2,
            "negative_space_ratio": 0.3,
            "kinetic_tempo": 0.35,
            "gravitational_anchor": 0.15,
        },
        "keywords": [
            "complex limb lattice creating structural framework from guard",
            "inverted body geometry with legs as primary control architecture",
            "small spiral hooks and frames maintaining spatial control",
            "hip-driven micro-adjustments within compressed engagement range",
            "layered defensive geometry with calculated apertures",
            "ground-anchored skeletal scaffolding of interwoven limbs",
        ],
    },
}

# =============================================================================
# CANONICAL STATES: Named positions in the parameter space
# =============================================================================

CANONICAL_STATES = {
    "ippon_seoi_nage": {
        "description": "Classic shoulder throw — peak judo arc, maximum vertical lift, explosive rotation",
        "art": "judo",
        "category": "throw",
        "coordinates": {
            "arc_radius": 0.9,
            "vertical_displacement": 0.85,
            "negative_space_ratio": 0.75,
            "kinetic_tempo": 0.9,
            "gravitational_anchor": 0.8,
        },
    },
    "osoto_gari": {
        "description": "Major outer reap — angular leg sweep, direct vertical drop, sharp impact",
        "art": "judo",
        "category": "throw",
        "coordinates": {
            "arc_radius": 0.6,
            "vertical_displacement": 0.8,
            "negative_space_ratio": 0.55,
            "kinetic_tempo": 0.85,
            "gravitational_anchor": 0.75,
        },
    },
    "uchi_mata": {
        "description": "Inner thigh throw — maximum sweeping arc, peak elevation, ballistic flight",
        "art": "judo",
        "category": "throw",
        "coordinates": {
            "arc_radius": 0.95,
            "vertical_displacement": 0.9,
            "negative_space_ratio": 0.8,
            "kinetic_tempo": 0.85,
            "gravitational_anchor": 0.9,
        },
    },
    "triangle_choke": {
        "description": "Sankaku-jime — iconic leg triangle, tight spiral compression, sustained squeeze",
        "art": "jiu_jitsu",
        "category": "submission",
        "coordinates": {
            "arc_radius": 0.15,
            "vertical_displacement": 0.1,
            "negative_space_ratio": 0.1,
            "kinetic_tempo": 0.2,
            "gravitational_anchor": 0.05,
        },
    },
    "kimura_lock": {
        "description": "Double wrist lock — figure-four shoulder isolation, controlled torque",
        "art": "jiu_jitsu",
        "category": "submission",
        "coordinates": {
            "arc_radius": 0.2,
            "vertical_displacement": 0.15,
            "negative_space_ratio": 0.2,
            "kinetic_tempo": 0.3,
            "gravitational_anchor": 0.1,
        },
    },
    "berimbolo": {
        "description": "Inverted guard sweep — flowing inversion, transitional spiral, creative movement",
        "art": "jiu_jitsu",
        "category": "sweep",
        "coordinates": {
            "arc_radius": 0.4,
            "vertical_displacement": 0.35,
            "negative_space_ratio": 0.35,
            "kinetic_tempo": 0.5,
            "gravitational_anchor": 0.3,
        },
    },
    "standing_exchange": {
        "description": "Tachi-waza opening — neutral grip fighting, maximum potential energy, open geometry",
        "art": "both",
        "category": "position",
        "coordinates": {
            "arc_radius": 0.5,
            "vertical_displacement": 0.7,
            "negative_space_ratio": 0.65,
            "kinetic_tempo": 0.4,
            "gravitational_anchor": 0.6,
        },
    },
}

# =============================================================================
# TECHNIQUE TAXONOMY: Complete vocabulary for deterministic lookup
# =============================================================================

TECHNIQUE_TAXONOMY = {
    "judo": {
        "te_waza": {  # hand techniques
            "seoi_nage": {"arc_radius": 0.85, "vertical_displacement": 0.85, "negative_space_ratio": 0.7, "kinetic_tempo": 0.9, "gravitational_anchor": 0.8},
            "tai_otoshi": {"arc_radius": 0.7, "vertical_displacement": 0.75, "negative_space_ratio": 0.6, "kinetic_tempo": 0.85, "gravitational_anchor": 0.7},
            "kata_guruma": {"arc_radius": 0.95, "vertical_displacement": 0.95, "negative_space_ratio": 0.85, "kinetic_tempo": 0.8, "gravitational_anchor": 0.9},
        },
        "koshi_waza": {  # hip techniques
            "ogoshi": {"arc_radius": 0.8, "vertical_displacement": 0.8, "negative_space_ratio": 0.55, "kinetic_tempo": 0.75, "gravitational_anchor": 0.75},
            "harai_goshi": {"arc_radius": 0.9, "vertical_displacement": 0.85, "negative_space_ratio": 0.75, "kinetic_tempo": 0.85, "gravitational_anchor": 0.85},
            "uchi_mata": {"arc_radius": 0.95, "vertical_displacement": 0.9, "negative_space_ratio": 0.8, "kinetic_tempo": 0.85, "gravitational_anchor": 0.9},
        },
        "ashi_waza": {  # foot/leg techniques
            "osoto_gari": {"arc_radius": 0.6, "vertical_displacement": 0.8, "negative_space_ratio": 0.55, "kinetic_tempo": 0.85, "gravitational_anchor": 0.75},
            "ouchi_gari": {"arc_radius": 0.5, "vertical_displacement": 0.6, "negative_space_ratio": 0.4, "kinetic_tempo": 0.7, "gravitational_anchor": 0.55},
            "deashi_harai": {"arc_radius": 0.65, "vertical_displacement": 0.5, "negative_space_ratio": 0.6, "kinetic_tempo": 0.95, "gravitational_anchor": 0.5},
            "kouchi_gari": {"arc_radius": 0.35, "vertical_displacement": 0.45, "negative_space_ratio": 0.35, "kinetic_tempo": 0.8, "gravitational_anchor": 0.4},
        },
        "sutemi_waza": {  # sacrifice techniques
            "tomoe_nage": {"arc_radius": 0.85, "vertical_displacement": 0.7, "negative_space_ratio": 0.7, "kinetic_tempo": 0.8, "gravitational_anchor": 0.65},
            "sumi_gaeshi": {"arc_radius": 0.7, "vertical_displacement": 0.55, "negative_space_ratio": 0.5, "kinetic_tempo": 0.75, "gravitational_anchor": 0.45},
            "yoko_guruma": {"arc_radius": 0.8, "vertical_displacement": 0.6, "negative_space_ratio": 0.6, "kinetic_tempo": 0.7, "gravitational_anchor": 0.5},
        },
    },
    "jiu_jitsu": {
        "submissions": {
            "triangle_choke": {"arc_radius": 0.15, "vertical_displacement": 0.1, "negative_space_ratio": 0.1, "kinetic_tempo": 0.2, "gravitational_anchor": 0.05},
            "armbar": {"arc_radius": 0.25, "vertical_displacement": 0.15, "negative_space_ratio": 0.15, "kinetic_tempo": 0.35, "gravitational_anchor": 0.1},
            "kimura": {"arc_radius": 0.2, "vertical_displacement": 0.15, "negative_space_ratio": 0.2, "kinetic_tempo": 0.3, "gravitational_anchor": 0.1},
            "rear_naked_choke": {"arc_radius": 0.1, "vertical_displacement": 0.1, "negative_space_ratio": 0.05, "kinetic_tempo": 0.15, "gravitational_anchor": 0.05},
            "guillotine": {"arc_radius": 0.2, "vertical_displacement": 0.3, "negative_space_ratio": 0.15, "kinetic_tempo": 0.4, "gravitational_anchor": 0.2},
            "omoplata": {"arc_radius": 0.3, "vertical_displacement": 0.15, "negative_space_ratio": 0.2, "kinetic_tempo": 0.25, "gravitational_anchor": 0.1},
        },
        "positions": {
            "closed_guard": {"arc_radius": 0.2, "vertical_displacement": 0.15, "negative_space_ratio": 0.2, "kinetic_tempo": 0.3, "gravitational_anchor": 0.1},
            "mount": {"arc_radius": 0.15, "vertical_displacement": 0.2, "negative_space_ratio": 0.15, "kinetic_tempo": 0.25, "gravitational_anchor": 0.1},
            "side_control": {"arc_radius": 0.15, "vertical_displacement": 0.15, "negative_space_ratio": 0.1, "kinetic_tempo": 0.2, "gravitational_anchor": 0.05},
            "back_control": {"arc_radius": 0.1, "vertical_displacement": 0.1, "negative_space_ratio": 0.05, "kinetic_tempo": 0.15, "gravitational_anchor": 0.05},
            "half_guard": {"arc_radius": 0.25, "vertical_displacement": 0.2, "negative_space_ratio": 0.25, "kinetic_tempo": 0.35, "gravitational_anchor": 0.15},
            "de_la_riva": {"arc_radius": 0.35, "vertical_displacement": 0.2, "negative_space_ratio": 0.35, "kinetic_tempo": 0.4, "gravitational_anchor": 0.15},
        },
        "sweeps": {
            "scissor_sweep": {"arc_radius": 0.45, "vertical_displacement": 0.35, "negative_space_ratio": 0.4, "kinetic_tempo": 0.6, "gravitational_anchor": 0.3},
            "hip_bump": {"arc_radius": 0.4, "vertical_displacement": 0.4, "negative_space_ratio": 0.45, "kinetic_tempo": 0.7, "gravitational_anchor": 0.35},
            "berimbolo": {"arc_radius": 0.4, "vertical_displacement": 0.35, "negative_space_ratio": 0.35, "kinetic_tempo": 0.5, "gravitational_anchor": 0.3},
            "flower_sweep": {"arc_radius": 0.5, "vertical_displacement": 0.4, "negative_space_ratio": 0.45, "kinetic_tempo": 0.55, "gravitational_anchor": 0.35},
        },
    },
}

# =============================================================================
# PRESETS: Oscillation patterns between canonical states
# =============================================================================

def _compute_sinusoidal_trajectory(state_a: Dict, state_b: Dict, steps: int) -> List[Dict]:
    """Compute sinusoidal interpolation trajectory between two states."""
    trajectory = []
    for i in range(steps):
        t = i / steps
        # Sinusoidal easing: slow at endpoints, fast in middle
        blend = 0.5 * (1 - math.cos(math.pi * t))
        point = {}
        for param in PARAMETER_NAMES:
            a_val = state_a[param]
            b_val = state_b[param]
            point[param] = a_val + (b_val - a_val) * blend
        trajectory.append(point)
    return trajectory


def _compute_triangular_trajectory(state_a: Dict, state_b: Dict, steps: int) -> List[Dict]:
    """Compute triangular (linear bounce) trajectory between two states."""
    trajectory = []
    for i in range(steps):
        t = i / steps
        # Triangle wave: linear up then linear down
        if t < 0.5:
            blend = t * 2
        else:
            blend = 2 * (1 - t)
        point = {}
        for param in PARAMETER_NAMES:
            a_val = state_a[param]
            b_val = state_b[param]
            point[param] = a_val + (b_val - a_val) * blend
        trajectory.append(point)
    return trajectory


def _compute_cycle_trajectory(states: List[Dict], steps_per_segment: int) -> List[Dict]:
    """Compute trajectory through multiple states in a cycle with sinusoidal easing."""
    trajectory = []
    n = len(states)
    for seg in range(n):
        state_a = states[seg]
        state_b = states[(seg + 1) % n]
        for i in range(steps_per_segment):
            t = i / steps_per_segment
            blend = 0.5 * (1 - math.cos(math.pi * t))
            point = {}
            for param in PARAMETER_NAMES:
                point[param] = state_a[param] + (state_b[param] - state_a[param]) * blend
            trajectory.append(point)
    return trajectory


PRESETS = {
    "randori_cycle": {
        "description": "Judo free practice: standing exchange → explosive throw → impact → reset to standing",
        "period": 24,
        "pattern": "cycle",
        "states": ["standing_exchange", "ippon_seoi_nage", "standing_exchange"],
        "trajectory": None,  # computed lazily
    },
    "roll_flow": {
        "description": "Jiu jitsu rolling: guard architecture → sweep → compression → submission → guard reset",
        "period": 20,
        "pattern": "cycle",
        "states": ["berimbolo", "triangle_choke", "berimbolo"],
        "trajectory": None,
    },
    "full_spectrum": {
        "description": "Complete standing→throw→ground→submission→reset limit cycle spanning both arts",
        "period": 32,
        "pattern": "cycle",
        "states": ["standing_exchange", "uchi_mata", "kimura_lock", "triangle_choke", "standing_exchange"],
        "trajectory": None,
    },
    "throw_pulse": {
        "description": "Sinusoidal oscillation between uchi_mata peak and standing exchange calm",
        "period": 18,
        "pattern": "sinusoidal",
        "state_a": "standing_exchange",
        "state_b": "uchi_mata",
        "trajectory": None,
    },
    "compression_wave": {
        "description": "Triangular oscillation between open guard and maximum submission compression",
        "period": 22,
        "pattern": "triangular",
        "state_a": "berimbolo",
        "state_b": "triangle_choke",
        "trajectory": None,
    },
}


def _get_preset_trajectory(preset_name: str) -> List[Dict]:
    """Compute and cache preset trajectory."""
    preset = PRESETS[preset_name]
    if preset["trajectory"] is not None:
        return preset["trajectory"]

    if preset["pattern"] == "cycle":
        state_coords = [CANONICAL_STATES[s]["coordinates"] for s in preset["states"]]
        steps_per = preset["period"] // len(preset["states"])
        trajectory = _compute_cycle_trajectory(state_coords, steps_per)
    elif preset["pattern"] == "sinusoidal":
        a = CANONICAL_STATES[preset["state_a"]]["coordinates"]
        b = CANONICAL_STATES[preset["state_b"]]["coordinates"]
        trajectory = _compute_sinusoidal_trajectory(a, b, preset["period"])
    elif preset["pattern"] == "triangular":
        a = CANONICAL_STATES[preset["state_a"]]["coordinates"]
        b = CANONICAL_STATES[preset["state_b"]]["coordinates"]
        trajectory = _compute_triangular_trajectory(a, b, preset["period"])
    else:
        trajectory = []

    preset["trajectory"] = trajectory
    return trajectory


# =============================================================================
# PHASE 2.6: Rhythmic Presets — Forced-Orbit Integration
# =============================================================================
#
# Phase 2.6 presets define forced-orbit oscillations between canonical states
# with GUARANTEED periodic closure and zero numerical drift. Each preset models
# a natural martial arts limit cycle:
#
#   randori_pulse (24):        Standing exchange ↔ shoulder throw — judo randori rhythm
#   ground_flow (20):          Berimbolo ↔ triangle choke — BJJ rolling rhythm
#   art_spectrum (30):         Shoulder throw ↔ triangle choke — full judo/BJJ spectrum
#   compression_release (16):  Standing exchange ↔ kimura lock — tension/release cycle
#   vertical_collapse (14):    Uchi mata (aerial) ↔ triangle choke (ground) — gravity cycle
#
# Periods: [14, 16, 20, 24, 30]
# =============================================================================

RHYTHMIC_PRESETS = {
    "randori_pulse": {
        "state_a": "standing_exchange",
        "state_b": "ippon_seoi_nage",
        "pattern": "sinusoidal",
        "num_cycles": 3,
        "steps_per_cycle": 24,
        "description": "Judo randori rhythm — neutral grip fighting builds into explosive shoulder throw, "
                       "then resets. Captures the standing exchange pulse of competitive judo.",
    },
    "ground_flow": {
        "state_a": "berimbolo",
        "state_b": "triangle_choke",
        "pattern": "sinusoidal",
        "num_cycles": 4,
        "steps_per_cycle": 20,
        "description": "BJJ rolling flow — open guard transitions collapse into tight submission "
                       "geometry then expand back. Models the breathing rhythm of ground work.",
    },
    "art_spectrum": {
        "state_a": "ippon_seoi_nage",
        "state_b": "triangle_choke",
        "pattern": "triangular",
        "num_cycles": 2,
        "steps_per_cycle": 30,
        "description": "Full judo-to-BJJ spectrum — sweeping aerial throw geometry descends linearly "
                       "into compressed ground submission, then reverses. The complete martial arts arc.",
    },
    "compression_release": {
        "state_a": "standing_exchange",
        "state_b": "kimura_lock",
        "pattern": "sinusoidal",
        "num_cycles": 5,
        "steps_per_cycle": 16,
        "description": "Tension-release cycle — open neutral distance collapses into locked joint "
                       "isolation, then releases. Rapid oscillation between freedom and control.",
    },
    "vertical_collapse": {
        "state_a": "uchi_mata",
        "state_b": "triangle_choke",
        "pattern": "square",
        "num_cycles": 4,
        "steps_per_cycle": 14,
        "description": "Gravity cycle — instantaneous transition from peak aerial displacement to "
                       "maximum ground compression. Models the binary of flight and entanglement.",
    },
}


def _generate_forced_orbit_oscillation(
    num_steps: int,
    num_cycles: float,
    pattern: str,
) -> np.ndarray:
    """Generate forced-orbit oscillation blend factors with guaranteed periodic closure.

    Uses np.linspace over full cycle count to ensure zero numerical drift.
    The oscillation maps [0, 1] as blend factor between state_a and state_b.

    Args:
        num_steps: Total number of trajectory steps.
        num_cycles: Number of full oscillation cycles.
        pattern: 'sinusoidal', 'triangular', or 'square'.

    Returns:
        np.ndarray of shape (num_steps,) with values in [0, 1].
    """
    if pattern == "sinusoidal":
        t = np.linspace(0.0, 2.0 * np.pi * num_cycles, num_steps, endpoint=False)
        return 0.5 * (1.0 - np.cos(t))

    elif pattern == "triangular":
        # Rational phase arithmetic avoids floating-point boundary errors
        alpha = np.empty(num_steps)
        for i in range(num_steps):
            phase = (num_cycles * i / num_steps) % 1.0
            alpha[i] = 2.0 * phase if phase < 0.5 else 2.0 * (1.0 - phase)
        return alpha

    elif pattern == "square":
        # Rational phase arithmetic for clean square wave
        alpha = np.empty(num_steps)
        for i in range(num_steps):
            phase = (num_cycles * i / num_steps) % 1.0
            alpha[i] = 0.0 if phase < 0.5 else 1.0
        return alpha

    else:
        raise ValueError(f"Unknown oscillation pattern: {pattern}")


def _generate_rhythmic_trajectory(preset_config: dict) -> List[Dict[str, float]]:
    """Generate a Phase 2.6 forced-orbit trajectory from a rhythmic preset config.

    Returns a list of dicts, each mapping parameter names to float values.
    Trajectory length = num_cycles * steps_per_cycle.
    Periodic closure is guaranteed by construction.
    """
    state_a_name = preset_config["state_a"]
    state_b_name = preset_config["state_b"]

    coords_a = CANONICAL_STATES[state_a_name]["coordinates"]
    coords_b = CANONICAL_STATES[state_b_name]["coordinates"]

    num_cycles = preset_config["num_cycles"]
    steps_per_cycle = preset_config["steps_per_cycle"]
    total_steps = num_cycles * steps_per_cycle

    vec_a = np.array([coords_a[p] for p in PARAMETER_NAMES])
    vec_b = np.array([coords_b[p] for p in PARAMETER_NAMES])

    alpha = _generate_forced_orbit_oscillation(
        total_steps, num_cycles, preset_config["pattern"]
    )

    # Interpolate: trajectory = (1 - alpha) * A + alpha * B
    trajectory_array = np.outer(1.0 - alpha, vec_a) + np.outer(alpha, vec_b)

    # Convert to list of dicts
    trajectory = []
    for row in trajectory_array:
        point = {p: float(row[i]) for i, p in enumerate(PARAMETER_NAMES)}
        trajectory.append(point)

    return trajectory


def _compute_closure_drift(
    trajectory: List[Dict[str, float]],
    steps_per_cycle: Optional[int] = None,
) -> float:
    """Compute closure drift of a forced-orbit trajectory.

    Measures cycle-to-cycle alignment: the Euclidean distance between
    trajectory[0] and trajectory[steps_per_cycle]. For a properly closed
    forced orbit this should be exactly 0.0.

    If steps_per_cycle is None, falls back to comparing first and last points.
    """
    if len(trajectory) < 2:
        return 0.0
    first = np.array([trajectory[0][p] for p in PARAMETER_NAMES])
    if steps_per_cycle is not None and len(trajectory) > steps_per_cycle:
        cycle2_start = np.array([trajectory[steps_per_cycle][p] for p in PARAMETER_NAMES])
        return float(np.linalg.norm(first - cycle2_start))
    else:
        last = np.array([trajectory[-1][p] for p in PARAMETER_NAMES])
        return float(np.linalg.norm(first - last))


# =============================================================================
# HELPER: Nearest visual type by Euclidean distance
# =============================================================================

def _euclidean_distance(a: Dict, b: Dict) -> float:
    """5D Euclidean distance between two coordinate dicts."""
    return math.sqrt(sum((a[p] - b[p]) ** 2 for p in PARAMETER_NAMES))


def _nearest_visual_type(coords: Dict) -> tuple:
    """Find nearest visual type and distance."""
    best_name = None
    best_dist = float("inf")
    for name, vtype in VISUAL_TYPES.items():
        d = _euclidean_distance(coords, vtype["coordinates"])
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name, best_dist


def _interpolate_keywords(coords: Dict, top_n: int = 3) -> List[str]:
    """Get blended keywords from nearest visual types weighted by proximity."""
    distances = []
    for name, vtype in VISUAL_TYPES.items():
        d = _euclidean_distance(coords, vtype["coordinates"])
        distances.append((name, d, vtype["keywords"]))
    distances.sort(key=lambda x: x[1])

    keywords = []
    for name, dist, kws in distances[:top_n]:
        weight = max(0, 1 - dist)  # simple linear falloff
        # Take keywords proportional to weight
        n_kw = max(1, int(len(kws) * weight))
        keywords.extend(kws[:n_kw])
    return keywords


def _coords_to_parameter_descriptors(coords: Dict) -> List[str]:
    """Generate human-readable parameter descriptions from coordinates."""
    descriptors = []

    ar = coords["arc_radius"]
    if ar > 0.7:
        descriptors.append(f"large sweeping arc radius ({ar:.2f})")
    elif ar > 0.4:
        descriptors.append(f"medium transitional arc ({ar:.2f})")
    else:
        descriptors.append(f"tight spiral radius ({ar:.2f})")

    vd = coords["vertical_displacement"]
    if vd > 0.7:
        descriptors.append(f"elevated aerial plane ({vd:.2f})")
    elif vd > 0.4:
        descriptors.append(f"mid-level transitional height ({vd:.2f})")
    else:
        descriptors.append(f"ground plane engagement ({vd:.2f})")

    ns = coords["negative_space_ratio"]
    if ns > 0.6:
        descriptors.append(f"open explosive separation ({ns:.2f})")
    elif ns > 0.3:
        descriptors.append(f"balanced contact-to-space ratio ({ns:.2f})")
    else:
        descriptors.append(f"dense body interlocking ({ns:.2f})")

    kt = coords["kinetic_tempo"]
    if kt > 0.7:
        descriptors.append(f"explosive burst tempo ({kt:.2f})")
    elif kt > 0.4:
        descriptors.append(f"moderate rhythmic tempo ({kt:.2f})")
    else:
        descriptors.append(f"sustained grinding pressure ({kt:.2f})")

    ga = coords["gravitational_anchor"]
    if ga > 0.6:
        descriptors.append(f"elevated unstable center of gravity ({ga:.2f})")
    elif ga > 0.3:
        descriptors.append(f"transitional weight distribution ({ga:.2f})")
    else:
        descriptors.append(f"low rooted gravitational anchor ({ga:.2f})")

    return descriptors


# =============================================================================
# RESPONSE FORMAT
# =============================================================================

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


# =============================================================================
# TOOL 1: get_visual_types — Layer 1 pure taxonomy lookup
# =============================================================================

@mcp.tool(
    name="get_martial_arts_visual_types",
    annotations={
        "title": "List Martial Arts Visual Types",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_martial_arts_visual_types() -> str:
    """List all martial arts visual types with their 5D coordinates and image-generation keywords.

    Layer 1: Pure taxonomy lookup (0 tokens).

    Returns the complete visual vocabulary catalog. Each visual type represents
    a region of the 5D martial arts parameter space with associated keywords
    suitable for image generation prompts.

    Returns:
        str: JSON with visual_types dict, count, and parameter_names.
    """
    return json.dumps(
        {
            "visual_types": {
                name: {
                    "coordinates": vt["coordinates"],
                    "keywords": vt["keywords"],
                    "keyword_count": len(vt["keywords"]),
                }
                for name, vt in VISUAL_TYPES.items()
            },
            "count": len(VISUAL_TYPES),
            "parameter_names": PARAMETER_NAMES,
        },
        indent=2,
    )


# =============================================================================
# TOOL 2: get_coordinates — Layer 1 pure taxonomy lookup
# =============================================================================

class GetCoordinatesInput(BaseModel):
    """Input for coordinate extraction."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(
        ...,
        description="Name of a canonical state (e.g. 'ippon_seoi_nage', 'triangle_choke') "
        "or a technique from the taxonomy (e.g. 'armbar', 'harai_goshi').",
        min_length=1,
        max_length=100,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format: 'json' or 'markdown'.",
    )


@mcp.tool(
    name="get_martial_arts_coordinates",
    annotations={
        "title": "Get Martial Arts Coordinates",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_martial_arts_coordinates(params: GetCoordinatesInput) -> str:
    """Extract normalized 5D parameter coordinates for a canonical state or technique.

    Layer 1: Pure taxonomy lookup (0 tokens).

    Accepts canonical state names or specific technique names from the taxonomy.
    Returns exact coordinates plus nearest visual type with distance metric.

    Args:
        params (GetCoordinatesInput): Contains name and response_format.

    Returns:
        str: Coordinates, source info, and nearest visual type.
    """
    name = params.name.lower().strip().replace(" ", "_").replace("-", "_")

    # Check canonical states first
    if name in CANONICAL_STATES:
        state = CANONICAL_STATES[name]
        coords = state["coordinates"]
        source = "canonical_state"
        meta = {"art": state["art"], "category": state["category"], "description": state["description"]}
    else:
        # Search technique taxonomy
        found = None
        found_art = None
        found_category = None
        for art, categories in TECHNIQUE_TAXONOMY.items():
            for category, techniques in categories.items():
                if name in techniques:
                    found = techniques[name]
                    found_art = art
                    found_category = category
                    break
            if found:
                break

        if found is None:
            return json.dumps({"error": f"Unknown technique or state: '{params.name}'", "available_canonical_states": list(CANONICAL_STATES.keys())})

        coords = found
        source = "technique_taxonomy"
        meta = {"art": found_art, "category": found_category}

    nearest_vt, distance = _nearest_visual_type(coords)

    result = {
        "name": name,
        "source": source,
        "coordinates": coords,
        "nearest_visual_type": nearest_vt,
        "distance_to_nearest": round(distance, 4),
        "metadata": meta,
    }

    if params.response_format == ResponseFormat.MARKDOWN:
        lines = [f"# {name}", f"**Source:** {source}"]
        for k, v in meta.items():
            lines.append(f"**{k}:** {v}")
        lines.append("\n## Coordinates")
        for p in PARAMETER_NAMES:
            lines.append(f"- {p}: {coords[p]:.2f}")
        lines.append(f"\n**Nearest visual type:** {nearest_vt} (distance: {distance:.4f})")
        return "\n".join(lines)

    return json.dumps(result, indent=2)


# =============================================================================
# TOOL 3: generate_attractor_prompt — Layer 2 deterministic vocabulary
# =============================================================================

class AttractorPromptMode(str, Enum):
    COMPOSITE = "composite"
    SPLIT_KEYWORDS = "split_keywords"
    DESCRIPTIVE = "descriptive"


class AttractorPromptInput(BaseModel):
    """Input for generating image-generation prompts from martial arts coordinates."""
    model_config = ConfigDict(extra="forbid")

    coordinates: Optional[Dict[str, float]] = Field(
        default=None,
        description="5D coordinates dict. Keys: arc_radius, vertical_displacement, "
        "negative_space_ratio, kinetic_tempo, gravitational_anchor. Values: 0.0-1.0. "
        "If omitted, use canonical_state.",
    )
    canonical_state: Optional[str] = Field(
        default=None,
        description="Name of a canonical state to use as source coordinates.",
    )
    mode: AttractorPromptMode = Field(
        default=AttractorPromptMode.COMPOSITE,
        description="'composite' = single blended prompt, 'split_keywords' = categorized lists, "
        "'descriptive' = narrative prompt paragraph.",
    )
    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Blending strength 0.0-1.0 (lower = more neutral vocabulary).",
    )


@mcp.tool(
    name="generate_martial_arts_attractor_prompt",
    annotations={
        "title": "Generate Martial Arts Attractor Prompt",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def generate_martial_arts_attractor_prompt(params: AttractorPromptInput) -> str:
    """Generate image-generation-ready prompts from 5D martial arts coordinates.

    Layer 2: Deterministic vocabulary extraction (0 tokens).

    Translates abstract parameter coordinates into concrete visual vocabulary
    suitable for Stable Diffusion, ComfyUI, DALL-E, or Midjourney.

    Three output modes:
    - composite: Single prompt string combining keywords and geometric specs.
    - split_keywords: Categorized keyword lists for prompt engineering.
    - descriptive: Narrative paragraph prompt for DALL-E / Midjourney.

    Args:
        params (AttractorPromptInput): Coordinates or canonical state, mode, strength.

    Returns:
        str: Image-generation prompt in requested format.
    """
    # Resolve coordinates
    if params.coordinates:
        coords = params.coordinates
    elif params.canonical_state:
        name = params.canonical_state.lower().strip().replace(" ", "_").replace("-", "_")
        if name in CANONICAL_STATES:
            coords = CANONICAL_STATES[name]["coordinates"]
        else:
            return json.dumps({"error": f"Unknown canonical state: '{params.canonical_state}'"})
    else:
        return json.dumps({"error": "Provide either coordinates or canonical_state"})

    # Apply strength (blend toward neutral 0.5)
    if params.strength < 1.0:
        coords = {
            p: 0.5 + (coords[p] - 0.5) * params.strength
            for p in PARAMETER_NAMES
        }

    # Get vocabulary
    nearest_vt, dist = _nearest_visual_type(coords)
    keywords = _interpolate_keywords(coords, top_n=3)
    descriptors = _coords_to_parameter_descriptors(coords)

    if params.mode == AttractorPromptMode.COMPOSITE:
        parts = keywords[:5] + descriptors[:3]
        prompt = ", ".join(parts)
        return json.dumps({
            "prompt": prompt,
            "nearest_visual_type": nearest_vt,
            "distance": round(dist, 4),
            "coordinates": coords,
        }, indent=2)

    elif params.mode == AttractorPromptMode.SPLIT_KEYWORDS:
        return json.dumps({
            "visual_type": nearest_vt,
            "visual_type_keywords": VISUAL_TYPES[nearest_vt]["keywords"],
            "interpolated_keywords": keywords,
            "parameter_descriptors": descriptors,
            "coordinates": coords,
            "distance": round(dist, 4),
        }, indent=2)

    else:  # descriptive
        # Build narrative paragraph
        ar_desc = "sweeping large-radius arcs" if coords["arc_radius"] > 0.6 else "tight controlled spirals" if coords["arc_radius"] < 0.3 else "medium transitional curves"
        vd_desc = "elevated through vertical space" if coords["vertical_displacement"] > 0.6 else "compressed onto the ground plane" if coords["vertical_displacement"] < 0.3 else "between standing and ground levels"
        ns_desc = "explosive open separation between bodies" if coords["negative_space_ratio"] > 0.6 else "densely interlocked with minimal air" if coords["negative_space_ratio"] < 0.3 else "balanced interplay of contact and space"
        kt_desc = "at explosive burst speed" if coords["kinetic_tempo"] > 0.6 else "with slow sustained pressure" if coords["kinetic_tempo"] < 0.3 else "at moderate rhythmic tempo"
        ga_desc = "with elevated unstable center of gravity" if coords["gravitational_anchor"] > 0.6 else "anchored low to the ground" if coords["gravitational_anchor"] < 0.3 else "with transitional weight distribution"

        narrative = (
            f"Two martial artists engaged in dynamic grappling, bodies describing {ar_desc} "
            f"{vd_desc}, {ns_desc}, moving {kt_desc}, {ga_desc}. "
            f"The composition emphasizes the geometry of human bodies as vectors of force and gravity, "
            f"with limbs tracing visible spiral paths through space."
        )

        return json.dumps({
            "prompt": narrative,
            "nearest_visual_type": nearest_vt,
            "coordinates": coords,
        }, indent=2)


# =============================================================================
# TOOL 4: get_technique_taxonomy — Layer 1 pure lookup
# =============================================================================

class TaxonomyInput(BaseModel):
    """Input for taxonomy browsing."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    art: Optional[str] = Field(
        default=None,
        description="Filter by art: 'judo' or 'jiu_jitsu'. Omit for all.",
    )
    category: Optional[str] = Field(
        default=None,
        description="Filter by category (e.g. 'submissions', 'koshi_waza'). Omit for all.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Output format.",
    )


@mcp.tool(
    name="get_martial_arts_taxonomy",
    annotations={
        "title": "Browse Martial Arts Technique Taxonomy",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_martial_arts_taxonomy(params: TaxonomyInput) -> str:
    """Browse the complete technique taxonomy with 5D coordinates per technique.

    Layer 1: Pure taxonomy lookup (0 tokens).

    Returns techniques organized by art and category, each with full 5D
    compositional coordinates for image generation mapping.

    Args:
        params (TaxonomyInput): Optional art and category filters.

    Returns:
        str: Technique taxonomy with coordinates.
    """
    result = {}
    for art_name, categories in TECHNIQUE_TAXONOMY.items():
        if params.art and art_name != params.art.lower().strip():
            continue
        art_result = {}
        for cat_name, techniques in categories.items():
            if params.category and cat_name != params.category.lower().strip():
                continue
            art_result[cat_name] = {
                t_name: t_coords for t_name, t_coords in techniques.items()
            }
        if art_result:
            result[art_name] = art_result

    if params.response_format == ResponseFormat.MARKDOWN:
        lines = ["# Martial Arts Technique Taxonomy"]
        for art_name, categories in result.items():
            lines.append(f"\n## {art_name.replace('_', ' ').title()}")
            for cat_name, techniques in categories.items():
                lines.append(f"\n### {cat_name.replace('_', ' ').title()}")
                for t_name, t_coords in techniques.items():
                    coord_str = ", ".join(f"{p}={v:.2f}" for p, v in t_coords.items())
                    lines.append(f"- **{t_name}**: {coord_str}")
        return "\n".join(lines)

    return json.dumps(result, indent=2)


# =============================================================================
# TOOL 5: compute_trajectory — Layer 2 deterministic interpolation
# =============================================================================

class TrajectoryInput(BaseModel):
    """Input for trajectory computation between two states."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    state_a: str = Field(..., description="Starting canonical state or technique name.")
    state_b: str = Field(..., description="Ending canonical state or technique name.")
    steps: int = Field(default=12, ge=4, le=48, description="Number of trajectory steps.")
    pattern: str = Field(
        default="sinusoidal",
        description="Interpolation pattern: 'sinusoidal' or 'triangular'.",
    )


def _resolve_coords(name: str) -> Optional[Dict]:
    """Resolve a name to coordinates from canonical states or taxonomy."""
    key = name.lower().strip().replace(" ", "_").replace("-", "_")
    if key in CANONICAL_STATES:
        return CANONICAL_STATES[key]["coordinates"]
    for art, categories in TECHNIQUE_TAXONOMY.items():
        for cat, techniques in categories.items():
            if key in techniques:
                return techniques[key]
    return None


@mcp.tool(
    name="compute_martial_arts_trajectory",
    annotations={
        "title": "Compute Martial Arts Trajectory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def compute_martial_arts_trajectory(params: TrajectoryInput) -> str:
    """Compute smooth interpolation trajectory between two martial arts states.

    Layer 2: Deterministic interpolation (0 tokens).

    Generates a sequence of 5D coordinates tracing a path between any two
    named states. Useful for animation, sequence composition, or orbit
    integration with aesthetic-dynamics-core.

    Args:
        params (TrajectoryInput): state_a, state_b, steps, pattern.

    Returns:
        str: JSON with trajectory array, metadata, and computed distances.
    """
    coords_a = _resolve_coords(params.state_a)
    coords_b = _resolve_coords(params.state_b)

    if coords_a is None:
        return json.dumps({"error": f"Unknown state: '{params.state_a}'"})
    if coords_b is None:
        return json.dumps({"error": f"Unknown state: '{params.state_b}'"})

    if params.pattern == "triangular":
        trajectory = _compute_triangular_trajectory(coords_a, coords_b, params.steps)
    else:
        trajectory = _compute_sinusoidal_trajectory(coords_a, coords_b, params.steps)

    total_distance = _euclidean_distance(coords_a, coords_b)

    return json.dumps({
        "state_a": params.state_a,
        "state_b": params.state_b,
        "pattern": params.pattern,
        "steps": params.steps,
        "total_distance": round(total_distance, 4),
        "trajectory": trajectory,
    }, indent=2)


# =============================================================================
# TOOL 6: list_presets — Layer 1 pure lookup
# =============================================================================

@mcp.tool(
    name="list_martial_arts_presets",
    annotations={
        "title": "List Martial Arts Rhythmic Presets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_martial_arts_presets() -> str:
    """List all available rhythmic presets with their parameters and trajectory data.

    Layer 1: Pure lookup (0 tokens).

    Presets represent curated oscillation patterns between canonical states,
    modeling the natural limit cycles of martial arts practice:
    standing→throw→ground→submission→reset.

    Returns:
        str: JSON with all presets including computed trajectories.
    """
    result = {}
    for name, preset in PRESETS.items():
        trajectory = _get_preset_trajectory(name)
        entry = {
            "description": preset["description"],
            "period": preset["period"],
            "pattern": preset["pattern"],
            "trajectory": trajectory,
        }
        if "states" in preset:
            entry["states"] = preset["states"]
        if "state_a" in preset:
            entry["state_a"] = preset["state_a"]
            entry["state_b"] = preset["state_b"]
        result[name] = entry

    return json.dumps(result, indent=2)


# =============================================================================
# TOOL 7: get_domain_registry_config — Tier 4D integration
# =============================================================================

@mcp.tool(
    name="get_martial_arts_domain_registry_config",
    annotations={
        "title": "Get Martial Arts Domain Registry Config",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_martial_arts_domain_registry_config() -> str:
    """Return Tier 4D integration configuration for compositional limit cycles.

    Layer 2: Pure lookup (0 tokens).

    Returns the domain signature for registering with aesthetic-dynamics-core
    multi-domain composition. Includes domain_id, parameter names, preset
    periods, and canonical state coordinates.

    Returns:
        str: JSON domain registry configuration.
    """
    # Compute all preset trajectories
    all_periods = sorted(set(p["period"] for p in PRESETS.values()))
    rhythmic_periods = sorted(set(p["steps_per_cycle"] for p in RHYTHMIC_PRESETS.values()))

    config = {
        "domain_id": "martial_arts_dynamics",
        "display_name": "Martial Arts Dynamics",
        "mcp_server": "martial_arts_dynamics_mcp",
        "parameter_names": PARAMETER_NAMES,
        "parameter_count": len(PARAMETER_NAMES),
        "canonical_states": {
            name: state["coordinates"]
            for name, state in CANONICAL_STATES.items()
        },
        "presets": {},
        "all_periods": all_periods,
        "visual_types": list(VISUAL_TYPES.keys()),
        "tier_4d_compatible": True,
        "phase_2_6": {
            "rhythmic_presets": True,
            "forced_orbit_integration": True,
            "zero_drift_guarantee": True,
            "preset_count": len(RHYTHMIC_PRESETS),
            "rhythmic_periods": rhythmic_periods,
            "oscillation_patterns": ["sinusoidal", "triangular", "square"],
        },
        "phase_2_7": {
            "attractor_visualization": True,
            "visualization_modes": ["composite", "sequence", "split_view"],
            "visual_type_count": len(VISUAL_TYPES),
        },
    }

    for preset_name, preset in PRESETS.items():
        trajectory = _get_preset_trajectory(preset_name)
        entry = {
            "period": preset["period"],
            "pattern": preset["pattern"],
            "trajectory": trajectory,
        }
        if "state_a" in preset:
            entry["state_a"] = preset["state_a"]
            entry["state_b"] = preset["state_b"]
        if "states" in preset:
            entry["states"] = preset["states"]
        config["presets"][preset_name] = entry

    return json.dumps(config, indent=2)


# =============================================================================
# PHASE 2.6 TOOL 8: apply_martial_arts_preset — Forced-orbit integration
# =============================================================================

class ApplyPresetInput(BaseModel):
    """Input for applying a Phase 2.6 rhythmic preset."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    preset_name: str = Field(
        ...,
        description="Name of the rhythmic preset to apply. Options: "
        "randori_pulse, ground_flow, art_spectrum, compression_release, vertical_collapse.",
    )
    num_cycles: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Override number of oscillation cycles (default: preset's own value).",
    )
    steps_per_cycle: Optional[int] = Field(
        default=None,
        ge=8,
        le=64,
        description="Override steps per cycle (default: preset's own value).",
    )


@mcp.tool(
    name="apply_martial_arts_preset",
    annotations={
        "title": "Apply Martial Arts Rhythmic Preset",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def apply_martial_arts_preset(params: ApplyPresetInput) -> str:
    """Apply a Phase 2.6 rhythmic preset, generating a complete forced-orbit trajectory.

    Layer 2: Deterministic NumPy computation (0 tokens).

    Generates a forced-orbit oscillation between two canonical states with
    GUARANTEED periodic closure and zero numerical drift. Each preset models
    a natural martial arts limit cycle.

    Available presets:
      randori_pulse (24):        Standing ↔ shoulder throw — judo randori rhythm
      ground_flow (20):          Berimbolo ↔ triangle choke — BJJ rolling flow
      art_spectrum (30):         Shoulder throw ↔ triangle choke — full spectrum
      compression_release (16):  Standing ↔ kimura lock — tension/release
      vertical_collapse (14):    Uchi mata ↔ triangle choke — gravity cycle

    Args:
        params: Preset name and optional cycle/step overrides.

    Returns:
        str: JSON with trajectory, metadata, closure drift, and bounds validation.
    """
    key = params.preset_name.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in RHYTHMIC_PRESETS:
        return json.dumps({
            "error": f"Unknown rhythmic preset: '{params.preset_name}'",
            "available_presets": list(RHYTHMIC_PRESETS.keys()),
        })

    base = RHYTHMIC_PRESETS[key]

    # Allow overrides
    config = {
        "state_a": base["state_a"],
        "state_b": base["state_b"],
        "pattern": base["pattern"],
        "num_cycles": params.num_cycles if params.num_cycles is not None else base["num_cycles"],
        "steps_per_cycle": params.steps_per_cycle if params.steps_per_cycle is not None else base["steps_per_cycle"],
    }

    total_steps = config["num_cycles"] * config["steps_per_cycle"]
    trajectory = _generate_rhythmic_trajectory(config)

    # Validate closure (cycle-to-cycle alignment)
    closure_drift = _compute_closure_drift(trajectory, config["steps_per_cycle"])

    # Validate bounds
    all_vals = [v for pt in trajectory for v in pt.values()]
    bounds_ok = all(0.0 <= v <= 1.0 for v in all_vals)

    return json.dumps({
        "preset": key,
        "description": base["description"],
        "state_a": config["state_a"],
        "state_b": config["state_b"],
        "pattern": config["pattern"],
        "num_cycles": config["num_cycles"],
        "steps_per_cycle": config["steps_per_cycle"],
        "total_steps": total_steps,
        "closure_drift": round(closure_drift, 10),
        "bounds_valid": bounds_ok,
        "trajectory": trajectory,
    }, indent=2)


# =============================================================================
# PHASE 2.6 TOOL 9: list_martial_arts_rhythmic_presets — Pure lookup
# =============================================================================

@mcp.tool(
    name="list_martial_arts_rhythmic_presets",
    annotations={
        "title": "List Martial Arts Phase 2.6 Rhythmic Presets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_martial_arts_rhythmic_presets() -> str:
    """List all available Phase 2.6 rhythmic presets with their parameters.

    Layer 1: Pure lookup (0 tokens).

    Returns preset names, oscillation patterns, periods, endpoint states,
    and cycle counts. Use this to discover available presets before calling
    apply_martial_arts_preset.

    Returns:
        str: JSON with all preset metadata and emergent attractor metadata.
    """
    result = {}
    for name, preset in RHYTHMIC_PRESETS.items():
        period = preset["steps_per_cycle"]
        total = preset["num_cycles"] * period
        result[name] = {
            "description": preset["description"],
            "state_a": preset["state_a"],
            "state_b": preset["state_b"],
            "pattern": preset["pattern"],
            "num_cycles": preset["num_cycles"],
            "steps_per_cycle": period,
            "total_steps": total,
            "period": period,
        }

    all_periods = sorted(set(p["steps_per_cycle"] for p in RHYTHMIC_PRESETS.values()))

    return json.dumps({
        "phase": "2.6",
        "preset_count": len(RHYTHMIC_PRESETS),
        "all_periods": all_periods,
        "period_range": [min(all_periods), max(all_periods)],
        "presets": result,
    }, indent=2)


# =============================================================================
# PHASE 2.6 TOOL 10: generate_martial_arts_rhythmic_sequence
# =============================================================================

class RhythmicSequenceInput(BaseModel):
    """Input for generating rhythmic oscillation between two states."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    state_a: str = Field(
        ...,
        description="First canonical state name (e.g. 'standing_exchange', 'ippon_seoi_nage').",
    )
    state_b: str = Field(
        ...,
        description="Second canonical state name (e.g. 'triangle_choke', 'uchi_mata').",
    )
    pattern: str = Field(
        default="sinusoidal",
        description="Oscillation pattern: 'sinusoidal', 'triangular', or 'square'.",
    )
    num_cycles: int = Field(default=3, ge=1, le=20, description="Number of oscillation cycles.")
    steps_per_cycle: int = Field(default=20, ge=8, le=64, description="Steps per oscillation cycle.")


@mcp.tool(
    name="generate_martial_arts_rhythmic_sequence",
    annotations={
        "title": "Generate Martial Arts Rhythmic Sequence",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def generate_martial_arts_rhythmic_sequence(params: RhythmicSequenceInput) -> str:
    """Generate rhythmic oscillation between two arbitrary canonical states.

    Layer 2: Deterministic NumPy computation (0 tokens).

    Like apply_martial_arts_preset but with custom endpoint selection.
    Useful for exploring oscillations between any two states, not just
    pre-curated presets.

    Args:
        params: Two state names, pattern, cycle count, and steps per cycle.

    Returns:
        str: JSON with trajectory, closure drift, and bounds validation.
    """
    name_a = params.state_a.lower().strip().replace(" ", "_").replace("-", "_")
    name_b = params.state_b.lower().strip().replace(" ", "_").replace("-", "_")

    if name_a not in CANONICAL_STATES:
        return json.dumps({
            "error": f"Unknown state: '{params.state_a}'",
            "available_states": list(CANONICAL_STATES.keys()),
        })
    if name_b not in CANONICAL_STATES:
        return json.dumps({
            "error": f"Unknown state: '{params.state_b}'",
            "available_states": list(CANONICAL_STATES.keys()),
        })

    if params.pattern not in ("sinusoidal", "triangular", "square"):
        return json.dumps({"error": f"Unknown pattern: '{params.pattern}'. Use sinusoidal, triangular, or square."})

    config = {
        "state_a": name_a,
        "state_b": name_b,
        "pattern": params.pattern,
        "num_cycles": params.num_cycles,
        "steps_per_cycle": params.steps_per_cycle,
    }

    total_steps = config["num_cycles"] * config["steps_per_cycle"]
    trajectory = _generate_rhythmic_trajectory(config)

    closure_drift = _compute_closure_drift(trajectory, config["steps_per_cycle"])

    all_vals = [v for pt in trajectory for v in pt.values()]
    bounds_ok = all(0.0 <= v <= 1.0 for v in all_vals)

    return json.dumps({
        "state_a": name_a,
        "state_b": name_b,
        "pattern": params.pattern,
        "num_cycles": params.num_cycles,
        "steps_per_cycle": params.steps_per_cycle,
        "total_steps": total_steps,
        "closure_drift": round(closure_drift, 10),
        "bounds_valid": bounds_ok,
        "trajectory": trajectory,
    }, indent=2)


# =============================================================================
# PHASE 2.7 TOOL 11: generate_attractor_visualization_prompt
# =============================================================================

class VisualizationMode(str, Enum):
    COMPOSITE = "composite"
    SEQUENCE = "sequence"
    SPLIT_VIEW = "split_view"


class AttractorVisualizationInput(BaseModel):
    """Input for Phase 2.7 attractor visualization prompt generation."""
    model_config = ConfigDict(extra="forbid")

    coordinates: Optional[Dict[str, float]] = Field(
        default=None,
        description="5D coordinates dict. If omitted, use preset_name to generate from trajectory.",
    )
    preset_name: Optional[str] = Field(
        default=None,
        description="Phase 2.6 preset name — generates prompt from trajectory midpoint and endpoints.",
    )
    canonical_state: Optional[str] = Field(
        default=None,
        description="Canonical state name for single-point prompt generation.",
    )
    mode: VisualizationMode = Field(
        default=VisualizationMode.COMPOSITE,
        description="'composite' = single blended prompt, 'sequence' = keyframe prompts across "
                    "trajectory, 'split_view' = separate prompts for each parameter extreme.",
    )
    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Vocabulary blending strength 0.0-1.0 (lower = more neutral).",
    )
    num_keyframes: int = Field(
        default=4,
        ge=2,
        le=12,
        description="Number of keyframes for sequence mode.",
    )


def _extract_visual_vocabulary_from_coords(
    coords: Dict[str, float],
    strength: float = 1.0,
) -> Dict[str, Any]:
    """Extract visual vocabulary from 5D coordinates via nearest-neighbor matching.

    Phase 2.7 core function. Maps morphospace coordinates to image-generation
    vocabulary by finding the nearest visual type and blending keywords from
    the closest types weighted by inverse distance.

    Returns dict with nearest_type, distance, keywords, and descriptors.
    """
    # Apply strength (blend toward neutral 0.5)
    if strength < 1.0:
        coords = {
            p: 0.5 + (coords.get(p, 0.5) - 0.5) * strength
            for p in PARAMETER_NAMES
        }

    nearest_vt, dist = _nearest_visual_type(coords)
    keywords = _interpolate_keywords(coords, top_n=3)
    descriptors = _coords_to_parameter_descriptors(coords)

    return {
        "nearest_type": nearest_vt,
        "distance": round(dist, 4),
        "keywords": keywords,
        "descriptors": descriptors,
        "coordinates": coords,
    }


def _build_composite_prompt(vocab: Dict[str, Any]) -> str:
    """Build a single composite image-generation prompt from extracted vocabulary."""
    parts = vocab["keywords"][:5] + vocab["descriptors"][:3]
    return ", ".join(parts)


def _build_descriptive_prompt(coords: Dict[str, float]) -> str:
    """Build a narrative descriptive prompt from raw coordinates."""
    ar = coords.get("arc_radius", 0.5)
    vd = coords.get("vertical_displacement", 0.5)
    ns = coords.get("negative_space_ratio", 0.5)
    kt = coords.get("kinetic_tempo", 0.5)
    ga = coords.get("gravitational_anchor", 0.5)

    ar_d = "sweeping large-radius arcs" if ar > 0.6 else "tight controlled spirals" if ar < 0.3 else "medium transitional curves"
    vd_d = "elevated through vertical space" if vd > 0.6 else "compressed onto the ground plane" if vd < 0.3 else "between standing and ground levels"
    ns_d = "explosive open separation between bodies" if ns > 0.6 else "densely interlocked with minimal air" if ns < 0.3 else "balanced interplay of contact and space"
    kt_d = "at explosive burst speed" if kt > 0.6 else "with slow sustained pressure" if kt < 0.3 else "at moderate rhythmic tempo"
    ga_d = "with elevated unstable center of gravity" if ga > 0.6 else "anchored low to the ground" if ga < 0.3 else "with transitional weight distribution"

    return (
        f"Two martial artists engaged in dynamic grappling, bodies describing {ar_d} "
        f"{vd_d}, {ns_d}, moving {kt_d}, {ga_d}. "
        f"The composition emphasizes the geometry of human bodies as vectors of force "
        f"and gravity, with limbs tracing visible spiral paths through space."
    )


@mcp.tool(
    name="generate_martial_arts_attractor_visualization_prompt",
    annotations={
        "title": "Generate Martial Arts Attractor Visualization Prompt (Phase 2.7)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def generate_martial_arts_attractor_visualization_prompt(
    params: AttractorVisualizationInput,
) -> str:
    """Generate image-generation-ready prompts from morphospace coordinates.

    Phase 2.7: Attractor visualization prompt generation (0 tokens).

    Translates 5D martial arts parameter coordinates into concrete visual
    vocabulary via nearest-neighbor matching against the visual type catalog.
    Supports three output modes for different image generation workflows:

    - composite: Single blended prompt from morphospace position.
    - sequence: Keyframe prompts sampled across a preset trajectory —
      generates a series of prompts that animate through the oscillation.
    - split_view: Separate prompts for state_a and state_b endpoints,
      plus a midpoint blend prompt.

    Args:
        params: Coordinates/preset/state, mode, strength, num_keyframes.

    Returns:
        str: JSON with generated prompts, vocabulary data, and coordinates.
    """
    # --- Resolve coordinates source ---
    if params.coordinates:
        # Direct coordinates mode
        if params.mode == VisualizationMode.SEQUENCE and params.preset_name is None:
            return json.dumps({"error": "Sequence mode requires preset_name (need a trajectory to sample)."})

        vocab = _extract_visual_vocabulary_from_coords(params.coordinates, params.strength)
        prompt = _build_composite_prompt(vocab)
        descriptive = _build_descriptive_prompt(vocab["coordinates"])

        return json.dumps({
            "mode": "composite",
            "prompt": prompt,
            "descriptive_prompt": descriptive,
            "nearest_visual_type": vocab["nearest_type"],
            "distance": vocab["distance"],
            "keywords": vocab["keywords"],
            "descriptors": vocab["descriptors"],
            "coordinates": vocab["coordinates"],
        }, indent=2)

    elif params.canonical_state:
        # Canonical state mode
        name = params.canonical_state.lower().strip().replace(" ", "_").replace("-", "_")
        if name not in CANONICAL_STATES:
            return json.dumps({
                "error": f"Unknown canonical state: '{params.canonical_state}'",
                "available_states": list(CANONICAL_STATES.keys()),
            })
        coords = CANONICAL_STATES[name]["coordinates"]
        vocab = _extract_visual_vocabulary_from_coords(coords, params.strength)
        prompt = _build_composite_prompt(vocab)
        descriptive = _build_descriptive_prompt(vocab["coordinates"])

        return json.dumps({
            "mode": "composite",
            "canonical_state": name,
            "prompt": prompt,
            "descriptive_prompt": descriptive,
            "nearest_visual_type": vocab["nearest_type"],
            "distance": vocab["distance"],
            "keywords": vocab["keywords"],
            "descriptors": vocab["descriptors"],
            "coordinates": vocab["coordinates"],
        }, indent=2)

    elif params.preset_name:
        # Preset-based mode — the richest path
        key = params.preset_name.lower().strip().replace(" ", "_").replace("-", "_")
        if key not in RHYTHMIC_PRESETS:
            return json.dumps({
                "error": f"Unknown preset: '{params.preset_name}'",
                "available_presets": list(RHYTHMIC_PRESETS.keys()),
            })

        preset = RHYTHMIC_PRESETS[key]
        config = {
            "state_a": preset["state_a"],
            "state_b": preset["state_b"],
            "pattern": preset["pattern"],
            "num_cycles": preset["num_cycles"],
            "steps_per_cycle": preset["steps_per_cycle"],
        }
        trajectory = _generate_rhythmic_trajectory(config)

        if params.mode == VisualizationMode.COMPOSITE:
            # Midpoint of first cycle
            mid_idx = len(trajectory) // 2
            mid_coords = trajectory[mid_idx]
            vocab = _extract_visual_vocabulary_from_coords(mid_coords, params.strength)
            prompt = _build_composite_prompt(vocab)
            descriptive = _build_descriptive_prompt(vocab["coordinates"])

            return json.dumps({
                "mode": "composite",
                "preset": key,
                "description": preset["description"],
                "sampled_at": f"step {mid_idx}/{len(trajectory)}",
                "prompt": prompt,
                "descriptive_prompt": descriptive,
                "nearest_visual_type": vocab["nearest_type"],
                "distance": vocab["distance"],
                "keywords": vocab["keywords"],
                "descriptors": vocab["descriptors"],
                "coordinates": vocab["coordinates"],
            }, indent=2)

        elif params.mode == VisualizationMode.SEQUENCE:
            # Sample keyframes evenly across one cycle
            cycle_len = config["steps_per_cycle"]
            keyframe_indices = [
                int(i * cycle_len / params.num_keyframes) for i in range(params.num_keyframes)
            ]

            keyframes = []
            for idx in keyframe_indices:
                kf_coords = trajectory[idx]
                vocab = _extract_visual_vocabulary_from_coords(kf_coords, params.strength)
                prompt = _build_composite_prompt(vocab)
                descriptive = _build_descriptive_prompt(vocab["coordinates"])
                keyframes.append({
                    "keyframe_index": idx,
                    "phase": round(idx / cycle_len, 3),
                    "prompt": prompt,
                    "descriptive_prompt": descriptive,
                    "nearest_visual_type": vocab["nearest_type"],
                    "distance": vocab["distance"],
                    "keywords": vocab["keywords"],
                    "coordinates": vocab["coordinates"],
                })

            return json.dumps({
                "mode": "sequence",
                "preset": key,
                "description": preset["description"],
                "period": config["steps_per_cycle"],
                "num_keyframes": params.num_keyframes,
                "keyframes": keyframes,
            }, indent=2)

        else:  # split_view
            # Separate prompts for state_a, state_b, and midpoint
            coords_a = CANONICAL_STATES[config["state_a"]]["coordinates"]
            coords_b = CANONICAL_STATES[config["state_b"]]["coordinates"]

            # Midpoint coordinates
            mid_coords = {
                p: (coords_a[p] + coords_b[p]) / 2.0
                for p in PARAMETER_NAMES
            }

            views = {}
            for label, c in [("state_a", coords_a), ("midpoint", mid_coords), ("state_b", coords_b)]:
                vocab = _extract_visual_vocabulary_from_coords(c, params.strength)
                prompt = _build_composite_prompt(vocab)
                descriptive = _build_descriptive_prompt(vocab["coordinates"])
                state_name = config.get(label, label)
                views[label] = {
                    "state_name": state_name if label != "midpoint" else "midpoint_blend",
                    "prompt": prompt,
                    "descriptive_prompt": descriptive,
                    "nearest_visual_type": vocab["nearest_type"],
                    "distance": vocab["distance"],
                    "keywords": vocab["keywords"],
                    "coordinates": vocab["coordinates"],
                }

            return json.dumps({
                "mode": "split_view",
                "preset": key,
                "description": preset["description"],
                "views": views,
            }, indent=2)

    else:
        return json.dumps({"error": "Provide one of: coordinates, canonical_state, or preset_name."})


# =============================================================================
# TOOL 12: get_server_info — Server metadata and capabilities
# =============================================================================

@mcp.tool(
    name="get_martial_arts_server_info",
    annotations={
        "title": "Get Martial Arts Dynamics Server Info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_martial_arts_server_info() -> str:
    """Get server metadata, capabilities, and Phase 2.6/2.7 status.

    Returns:
        str: JSON with server version, domain info, and feature status.
    """
    all_periods = sorted(set(p["steps_per_cycle"] for p in RHYTHMIC_PRESETS.values()))

    return json.dumps({
        "server": "martial_arts_dynamics_mcp",
        "version": "2.7.0",
        "author": "Dal Marsters / Lushy Project",
        "description": "Martial arts visual dynamics — judo/jiu jitsu geometry mapped to "
                       "5D compositional parameter space for image generation.",
        "parameter_space": {
            "dimensions": 5,
            "parameter_names": PARAMETER_NAMES,
            "range": "[0.0, 1.0] per dimension",
        },
        "taxonomy": {
            "canonical_states": len(CANONICAL_STATES),
            "visual_types": len(VISUAL_TYPES),
            "technique_categories": sum(
                len(cats) for cats in TECHNIQUE_TAXONOMY.values()
            ),
            "total_techniques": sum(
                len(techs) for cats in TECHNIQUE_TAXONOMY.values() for techs in cats.values()
            ),
        },
        "phase_2_6_enhancements": {
            "rhythmic_presets": True,
            "forced_orbit_integration": True,
            "zero_drift_guarantee": True,
            "preset_count": len(RHYTHMIC_PRESETS),
            "available_presets": list(RHYTHMIC_PRESETS.keys()),
            "all_periods": all_periods,
            "period_range": [min(all_periods), max(all_periods)],
            "oscillation_patterns": ["sinusoidal", "triangular", "square"],
        },
        "phase_2_7_enhancements": {
            "attractor_visualization": True,
            "visualization_modes": ["composite", "sequence", "split_view"],
            "visual_type_count": len(VISUAL_TYPES),
            "nearest_neighbor_matching": True,
            "keyword_interpolation": True,
        },
        "tier_4d_compatible": True,
        "tools": [
            "get_martial_arts_visual_types",
            "get_martial_arts_coordinates",
            "generate_martial_arts_attractor_prompt",
            "get_martial_arts_taxonomy",
            "compute_martial_arts_trajectory",
            "list_martial_arts_presets",
            "get_martial_arts_domain_registry_config",
            "apply_martial_arts_preset",
            "list_martial_arts_rhythmic_presets",
            "generate_martial_arts_rhythmic_sequence",
            "generate_martial_arts_attractor_visualization_prompt",
            "get_martial_arts_server_info",
        ],
    }, indent=2)


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    mcp.run()

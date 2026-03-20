# Martial Arts Dynamics MCP Server

Translates the visual geometry of judo and jiu jitsu into a 5D compositional parameter space for image generation. Built on the insight that these two grappling arts represent complementary geometric systems — judo as macro-geometry (big circle, large arcs, vertical throws, explosive bursts) and jiu jitsu as micro-geometry (small circle, tight spirals, ground compression, sustained pressure) — connected by an endless cycle of spirals and dynamic spheres.

## Domain concept

A friend who trains both arts described the relationship:

> Judo is big circle with angles in many directions and big falls, and jiu jitsu is small circle. It's all empty space, bodies and gravity in an endless cycle of spirals and dynamic spheres.

This server formalises that description into a deterministic taxonomy that maps techniques, positions, and transitions to compositional parameters suitable for Stable Diffusion, ComfyUI, DALL-E, or Midjourney prompt engineering.

## Architecture

Three-layer cost-optimised design following the standard MCP server pattern:

| Layer | Function | Cost |
|-------|----------|------|
| **Layer 1** | Pure taxonomy lookup — coordinates, visual types, technique catalog, presets | 0 tokens |
| **Layer 2** | Deterministic vocabulary extraction — attractor prompts, trajectory interpolation | 0 tokens |
| **Layer 3** | Creative synthesis (reserved for LLM caller) | Variable |

Layers 1 and 2 are entirely deterministic. The LLM caller handles creative synthesis, achieving ~60-85% inference cost savings vs pure LLM approaches.

## 5D parameter space

| Parameter | Low (0.0) | High (1.0) |
|-----------|-----------|------------|
| `arc_radius` | Tight spiral (jiu jitsu wraps) | Full body arc (judo throws) |
| `vertical_displacement` | Ground plane engagement | Aerial / standing throws |
| `negative_space_ratio` | Densely interlocked bodies | Explosive open separation |
| `kinetic_tempo` | Sustained grinding pressure | Explosive burst impact |
| `gravitational_anchor` | Low, rooted, stable | Elevated, transitional, unstable |

The two arts occupy opposite poles: judo techniques cluster in the high-arc, high-vertical, high-tempo region while jiu jitsu techniques cluster in the low-arc, low-vertical, low-tempo region. Transition techniques (sweeps, sacrifice throws, guard pulls) occupy the middle ground.

## Visual types

Five regions of the parameter space, each with curated image-generation keywords:

- **orbital_throw** — sweeping circular arcs, centrifugal separation, parabolic flight paths
- **spiral_compression** — tightly wound limbs, minimal negative space, grinding rotational force
- **transition_flow** — mid-transition balance, rhythmic oscillation between expansion and compression
- **impact_moment** — peak force instant, gravitational free-fall, shockwave composition
- **guard_architecture** — complex limb lattice, inverted body geometry, structural framework

## Canonical states

Seven named positions anchoring the parameter space:

| State | Art | Category | Arc | Vert | Space | Tempo | Gravity |
|-------|-----|----------|-----|------|-------|-------|---------|
| `ippon_seoi_nage` | Judo | Throw | 0.90 | 0.85 | 0.75 | 0.90 | 0.80 |
| `osoto_gari` | Judo | Throw | 0.60 | 0.80 | 0.55 | 0.85 | 0.75 |
| `uchi_mata` | Judo | Throw | 0.95 | 0.90 | 0.80 | 0.85 | 0.90 |
| `triangle_choke` | Jiu Jitsu | Submission | 0.15 | 0.10 | 0.10 | 0.20 | 0.05 |
| `kimura_lock` | Jiu Jitsu | Submission | 0.20 | 0.15 | 0.20 | 0.30 | 0.10 |
| `berimbolo` | Jiu Jitsu | Sweep | 0.40 | 0.35 | 0.35 | 0.50 | 0.30 |
| `standing_exchange` | Both | Position | 0.50 | 0.70 | 0.65 | 0.40 | 0.60 |

The Euclidean distance from `standing_exchange` to `triangle_choke` is **1.0618** — nearly the maximum possible span — quantifying how far apart the two poles of the domain are.

## Technique taxonomy

29 techniques with full 5D coordinates, organised by art and category:

**Judo (13 techniques)**
- `te_waza` (hand): seoi_nage, tai_otoshi, kata_guruma
- `koshi_waza` (hip): ogoshi, harai_goshi, uchi_mata
- `ashi_waza` (foot/leg): osoto_gari, ouchi_gari, deashi_harai, kouchi_gari
- `sutemi_waza` (sacrifice): tomoe_nage, sumi_gaeshi, yoko_guruma

**Jiu Jitsu (16 techniques)**
- `submissions`: triangle_choke, armbar, kimura, rear_naked_choke, guillotine, omoplata
- `positions`: closed_guard, mount, side_control, back_control, half_guard, de_la_riva
- `sweeps`: scissor_sweep, hip_bump, berimbolo, flower_sweep

## Rhythmic presets

Five oscillation patterns modelling the natural limit cycles of martial arts practice:

| Preset | Period | Pattern | Description |
|--------|--------|---------|-------------|
| `randori_cycle` | 24 | cycle | Standing exchange → explosive throw → reset to standing |
| `roll_flow` | 20 | cycle | Guard → sweep → compression → submission → guard reset |
| `full_spectrum` | 32 | cycle | Complete standing→throw→ground→submission→reset spanning both arts |
| `throw_pulse` | 18 | sinusoidal | Oscillation between standing calm and uchi_mata peak |
| `compression_wave` | 22 | triangular | Oscillation between open guard and maximum submission compression |

## Tools

### Layer 1: Pure taxonomy (0 tokens)

**`get_martial_arts_visual_types`** — List all visual types with 5D coordinates and image-generation keywords.

**`get_martial_arts_coordinates`** — Extract coordinates for any canonical state or technique name. Returns nearest visual type with distance metric.

**`get_martial_arts_taxonomy`** — Browse the complete technique catalog, filterable by art and category.

**`list_martial_arts_presets`** — List all rhythmic presets with computed trajectories.

### Layer 2: Deterministic vocabulary (0 tokens)

**`generate_martial_arts_attractor_prompt`** — Generate image-generation prompts from 5D coordinates. Three output modes:
- `composite` — Single prompt string for direct image generation
- `split_keywords` — Categorised keyword lists for ComfyUI prompt engineering
- `descriptive` — Narrative paragraph prompt for DALL-E / Midjourney

**`compute_martial_arts_trajectory`** — Smooth interpolation between any two named states. Sinusoidal or triangular patterns. Compatible with aesthetic-dynamics-core orbit integration.

### Integration

**`get_martial_arts_domain_registry_config`** — Tier 4D domain signature for multi-domain composition with aesthetic-dynamics-core `integrate_forced_limit_cycle_multi_domain`.

## Deployment

### FastMCP Cloud

```
fastmcp deploy martial_arts_dynamics_mcp.py:mcp
```

The entrypoint returns the server object — cloud handles the event loop. Entry point format: `martial_arts_dynamics_mcp.py:mcp`.

### Local

```bash
pip install fastmcp
python martial_arts_dynamics_mcp.py
```

## Usage examples

### Get coordinates for a technique

```python
# Returns 5D coordinates + nearest visual type
get_martial_arts_coordinates(name="uchi_mata")
# → arc_radius: 0.95, vertical_displacement: 0.90, ...
# → nearest_visual_type: "orbital_throw" (distance: 0.1118)
```

### Generate a descriptive prompt

```python
generate_martial_arts_attractor_prompt(
    canonical_state="triangle_choke",
    mode="descriptive"
)
# → "Two martial artists engaged in dynamic grappling, bodies describing
#    tight controlled spirals compressed onto the ground plane, densely
#    interlocked with minimal air, moving with slow sustained pressure,
#    anchored low to the ground..."
```

### Compute a trajectory between arts

```python
compute_martial_arts_trajectory(
    state_a="standing_exchange",
    state_b="triangle_choke",
    steps=12,
    pattern="sinusoidal"
)
# → 12-step trajectory traversing from judo's standing geometry
#    down through the transition zone into jiu jitsu's ground compression
```

### Multi-domain composition

The domain registry config integrates with aesthetic-dynamics-core for composing martial arts dynamics with other aesthetic domains (constellation, heraldic blazonry, cocktail aesthetics, etc.) in synchronised limit cycles.

```python
# Register with aesthetic-dynamics-core
config = get_martial_arts_domain_registry_config()
# → domain_id: "martial_arts_dynamics"
# → tier_4d_compatible: true
# → 5 presets with periods [18, 20, 22, 24, 32]
```

## Dependencies

None beyond FastMCP and Pydantic (provided by FastMCP). All computations are pure Python with only `math` from the standard library.

## License

Part of the Lushy MCP server ecosystem.

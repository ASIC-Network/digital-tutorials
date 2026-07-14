<!--
  ASIC Network docs page. quick rules:
  - filename must be page_N.md, numbered with no gaps (page_1.md, page_2.md, ...)
  - the first "# Heading" becomes this page's name in the sidebar, one H1 per page
  - raw HTML is not rendered, stick to markdown (this comment is stripped)
  - images live in the repo (e.g. img/...) and are referenced by relative path
  - copy TEMPLATE.md to start a new page
-->

# Ring Oscillator

A 5-stage ring oscillator on SKY130, from schematic to simulated frequency. This page doubles as the **formatting reference**: every construct the renderer understands is used somewhere below.

> **TL;DR**: an odd number of inverters in a loop has no stable DC operating point, so it oscillates at roughly `f = 1 / (2 * N * t_pd)`. Five stages of the standard inverter lands near 1.2 GHz at tt.

## Overview

The ring oscillator is the *hello world* of analog design: it needs correct device models, a working simulator, and nothing else. If this page simulates cleanly, your [toolchain setup](page_2.md) is good and every later tutorial will run.

Inline styles for reference: **bold**, *italic*, ***both***, `inline code`, ~~struck~~, and an external link to the [SKY130 PDK docs](https://skywater-pdk.readthedocs.io).

## Prerequisites

- `xschem` and `ngspice` installed and on `$PATH`
- SKY130A PDK with `$PDK_ROOT` exported
  - built with `open_pdks`
  - includes the `sky130_fd_pr` primitives library
- Basic familiarity with SPICE netlists

## Schematic

![5-stage ring oscillator](img/ring_osc_schematic.png "Five inverters in a loop, buffered output")

Keep the loop symmetric: identical `W/L` on every stage, and buffer the tap so the probe capacitance does not load the ring.

## Netlist

```spice
* ring_osc.spice : 5-stage ring oscillator, sky130 tt
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice tt

.subckt inv in out vdd gnd
XM1 out in gnd gnd sky130_fd_pr__nfet_01v8 W=1   L=0.15
XM2 out in vdd vdd sky130_fd_pr__pfet_01v8 W=2.1 L=0.15
.ends

Xi1 n5 n1 vdd 0 inv
Xi2 n1 n2 vdd 0 inv
Xi3 n2 n3 vdd 0 inv
Xi4 n3 n4 vdd 0 inv
Xi5 n4 n5 vdd 0 inv

Vdd vdd 0 1.8
.ic v(n1)=0
.tran 10p 20n
.end
```

## Run it

1. Export the environment
   1. `export PDK_ROOT=/usr/local/share/pdk`
2. Launch the simulation
   1. `ngspice ring_osc.spice`
   2. wait for the transient to finish
3. Measure the period on `v(n5)` and invert it

## Results

| Corner | VDD | f_osc | Power |
|:-------|:---:|------:|------:|
| tt | 1.80 V | 1.21 GHz | 84 uW |
| ss | 1.62 V | 0.89 GHz | 61 uW |
| ff | 1.98 V | 1.63 GHz | 118 uW |

Frequency tracks `1/t_pd`, so expect roughly linear movement with VDD across corners.

## Checklist

- [x] schematic drawn, ERC clean
- [x] transient runs at tt
- [ ] ss / ff corners swept
- [ ] layout drawn, DRC and LVS clean

---

## Further reading

- [SKY130 device documentation](https://skywater-pdk.readthedocs.io)
- [ngspice manual](https://ngspice.sourceforge.io/docs.html)
- next up: [toolchain setup](page_2.md)

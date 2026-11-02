# Suspension starter files

Stock rear suspension carrying the added rear mass (pack, rear drive unit, mounts).
Mentor: Geoffrey Chavez. Guide: `docs/guides/suspension.html` on the taskline site.

| File | What it does | Task |
|---|---|---|
| `susp_params.m` | All inputs. `'cherokee'` = real values, with `NaN` where unmeasured. `'example'` = teaching numbers only. | ST-17 fills the Cherokee set |
| `susp_handcalcs.m` | The eight hand calculations, printed in order | ST-18 to ST-22 check against it |
| `quarter_car_ode.m` | Quarter-car model with `ode45` (no Simulink). Reference answer and percent error vs the hand calc | ST-20, ST-23 |
| `build_quarter_car_slx.m` | Builds `quarter_car.slx` from basic blocks and compares it with the ode45 answer | ST-23 |

## Run it

```matlab
cd matlab/suspension
susp_handcalcs('example')        % runs today, teaching numbers
quarter_car_ode('example')       % reference model and percent error
build_quarter_car_slx('example') % Simulink version (needs Simulink)
susp_handcalcs('cherokee')       % stops and lists what ST-17 still has to measure
```

## Status

- `susp_handcalcs.m` and `quarter_car_ode.m` were run in GNU Octave on the example set. They have not yet been run in MATLAB.
- `build_quarter_car_slx.m` has **not been run in Simulink yet**. The first successful run is part of ST-23.
- **The `'example'` numbers are not Cherokee data.** Never put them in a report or deliverable.

## Rules

- Inputs change in `susp_params.m` only. Every value carries a source in its comment.
- Motion ratio = spring travel / wheel travel, so wheel rate = spring rate × MR².
- Generated `.slx` files and `.mat` data are not committed.

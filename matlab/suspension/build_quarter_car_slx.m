function build_quarter_car_slx(set_name, which_rear)
%BUILD_QUARTER_CAR_SLX  Build the quarter-car Simulink model from blocks (ST-23).
%
%   build_quarter_car_slx('example')            converted rear corner
%   build_quarter_car_slx('example', 'stock')   stock rear corner
%
%   Builds quarter_car.slx from basic Simulink blocks (Integrator, Gain, Sum,
%   Step, To Workspace), so the model is reproducible from this script and no
%   binary .slx has to live in Git. Then simulates a 20 mm road step and
%   compares it with quarter_car_ode.m.
%
%   STATUS: written against documented Simulink commands but NOT YET RUN in
%   Simulink. The first successful run is part of task ST-23. If a line fails,
%   fix it, note the MATLAB release, and commit the fix.
%
%   Equations (from static equilibrium, so no gravity):
%       ms*zs'' = -Fs            Fs = Kw*(zs-zu) + cw*(zs'-zu')
%       mu*zu'' =  Fs - Ft       Ft = kt*(zu-zr)

if nargin < 1, set_name = 'example'; end
if nargin < 2, which_rear = 'converted'; end
H = susp_handcalcs(set_name, 0.4, 0.6, true);
P = susp_params(set_name);
k = 2 - strcmpi(which_rear, 'stock');

% Parameters go to the base workspace; block dialogs hold names, not numbers.
assignin('base', 'ms', H.ms_corner(k));
assignin('base', 'mu', P.m_u_r);
assignin('base', 'Kw', H.wheel_rate);
assignin('base', 'cw', P.c_d_r * P.MRd_r^2);
assignin('base', 'kt', P.k_t);
assignin('base', 'zr_step', 0.020);

mdl = 'quarter_car';
if bdIsLoaded(mdl), close_system(mdl, 0); end
new_system(mdl);
set_param(mdl, 'Solver', 'ode45', 'StopTime', '4', 'MaxStep', '1e-3');

b = @(name) [mdl '/' name];
add_block('simulink/Sources/Step',            b('Road'),    'Time', '0.5', 'Before', '0', 'After', 'zr_step');
add_block('simulink/Math Operations/Sum',     b('d_rel'),   'Inputs', '+-');   % zs - zu
add_block('simulink/Math Operations/Sum',     b('v_rel'),   'Inputs', '+-');   % zs' - zu'
add_block('simulink/Math Operations/Gain',    b('Spring'),  'Gain', 'Kw');
add_block('simulink/Math Operations/Gain',    b('Damper'),  'Gain', 'cw');
add_block('simulink/Math Operations/Sum',     b('Fs'),      'Inputs', '++');
add_block('simulink/Math Operations/Gain',    b('Body_acc'),'Gain', '-1/ms');
add_block('simulink/Continuous/Integrator',   b('zs_dot'));
add_block('simulink/Continuous/Integrator',   b('zs'));
add_block('simulink/Math Operations/Sum',     b('tire_def'),'Inputs', '+-');   % zu - zr
add_block('simulink/Math Operations/Gain',    b('Tire'),    'Gain', 'kt');
add_block('simulink/Math Operations/Sum',     b('F_wheel'), 'Inputs', '+-');   % Fs - Ft
add_block('simulink/Math Operations/Gain',    b('Wheel_acc'),'Gain', '1/mu');
add_block('simulink/Continuous/Integrator',   b('zu_dot'));
add_block('simulink/Continuous/Integrator',   b('zu'));
add_block('simulink/Sinks/To Workspace',      b('log_zs'),  'VariableName', 'zs_out', 'SaveFormat', 'Array');
add_block('simulink/Sinks/To Workspace',      b('log_zu'),  'VariableName', 'zu_out', 'SaveFormat', 'Array');

L = @(a, c) add_line(mdl, a, c, 'autorouting', 'on');
% body
L('Fs/1', 'Body_acc/1');      L('Body_acc/1', 'zs_dot/1');  L('zs_dot/1', 'zs/1');
% wheel
L('Fs/1', 'F_wheel/1');       L('Tire/1', 'F_wheel/2');
L('F_wheel/1', 'Wheel_acc/1');L('Wheel_acc/1', 'zu_dot/1'); L('zu_dot/1', 'zu/1');
% suspension force
L('zs/1', 'd_rel/1');         L('zu/1', 'd_rel/2');
L('zs_dot/1', 'v_rel/1');     L('zu_dot/1', 'v_rel/2');
L('d_rel/1', 'Spring/1');     L('v_rel/1', 'Damper/1');
L('Spring/1', 'Fs/1');        L('Damper/1', 'Fs/2');
% tire force
L('zu/1', 'tire_def/1');      L('Road/1', 'tire_def/2');    L('tire_def/1', 'Tire/1');
% logging
L('zs/1', 'log_zs/1');        L('zu/1', 'log_zu/1');

try
    Simulink.BlockDiagram.arrangeSystem(mdl);
catch
end
save_system(mdl);
open_system(mdl);

% Simulate and compare with the ODE reference
out = sim(mdl, 'ReturnWorkspaceOutputs', 'on');
t = out.tout;  zs = out.zs_out;
Q = quarter_car_ode(set_name, which_rear);
zs_ref = interp1(Q.t, Q.zs, t);
fprintf('Simulink vs ode45: max body difference %.3f mm\n', 1e3*max(abs(zs - zs_ref)));
figure('Name', 'Simulink vs ode45');
plot(t, 1e3*zs, Q.t, 1e3*Q.zs, '--'); grid on;
xlabel('Time (s)'); ylabel('Body displacement (mm)');
legend('Simulink', 'ode45 reference', 'Location', 'southeast');
end

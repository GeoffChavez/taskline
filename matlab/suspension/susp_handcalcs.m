function R = susp_handcalcs(set_name, a_long, a_lat, quiet)
%SUSP_HANDCALCS  The eight suspension hand calculations, in order.
%
%   R = susp_handcalcs('cherokee')       real inputs (stops if any are missing)
%   R = susp_handcalcs('example')        teaching example, runs today
%   R = susp_handcalcs(set, a_long, a_lat)  accelerations in g (default 0.4, 0.6)
%
%   Every number printed here should also be done by hand once (tasks ST-18 to
%   ST-22). The script is the check on the hand calc, not a replacement for it.
%   Works in MATLAB and GNU Octave. No toolboxes needed.

if nargin < 1, set_name = 'example'; end
if nargin < 2, a_long = 0.4; end
if nargin < 3, a_lat  = 0.6; end
if nargin < 4, quiet  = false; end
P = susp_params(set_name);
g = P.g;
check_inputs(P);

%% 1. Axle loads and CG, stock vs converted (ST-18)
m0  = P.m_curb;
Wr0 = m0 * g * (1 - P.wf);              % N, rear axle, stock
x0  = (1 - P.wf) * P.L;                 % m, CG behind front axle, stock
madd = sum([P.added.m]);
mx   = sum([P.added.m] .* [P.added.x]);
m1  = m0 + madd - P.removed_rear;
x1  = (m0*x0 + mx - P.removed_rear*P.L) / m1;  % new CG position from front axle
Wr1 = m1 * g * x1 / P.L;
Wf1 = m1 * g - Wr1;
R.mass_added  = madd;
R.mass_net    = madd - P.removed_rear;
R.within_allowance = R.mass_net <= P.m_add_max;
R.cg_x  = [x0 x1];
R.Wr    = [Wr0 Wr1];
R.Wf    = [m0*g - Wr0, Wf1];
R.rear_fraction = [Wr0/(m0*g), Wr1/(m1*g)];

%% 2. Wheel rate and ride rate (ST-19)
Kw = P.k_s_r * P.MR_r^2;                % N/m at the wheel
Kr = Kw * P.k_t / (Kw + P.k_t);         % springs in series with the tire
R.wheel_rate = Kw;
R.ride_rate  = Kr;

%% 3. Static ride-height drop at each rear corner (ST-19)
dW_corner = (Wr1 - Wr0) / 2;            % N per rear corner
R.drop_rear = dW_corner / Kr;           % m, body drop at the rear (spring + tire)

%% 4. Ride frequency and damping ratio (ST-20)
ms0 = Wr0/2/g - P.m_u_r;                % kg, sprung mass per rear corner
ms1 = Wr1/2/g - P.m_u_r;
cw  = P.c_d_r * P.MRd_r^2;              % N*s/m at the wheel
R.ms_corner = [ms0 ms1];
R.f_ride  = sqrt(Kr ./ [ms0 ms1]) / (2*pi);          % Hz
R.zeta    = cw ./ (2*sqrt(Kr .* [ms0 ms1]));         % quarter-car approximation
R.f_wheelhop = sqrt((Kw + P.k_t)/P.m_u_r) / (2*pi);  % Hz, unsprung mode

%% 5. Load transfer (ST-21)
W1 = m1 * g;
R.dW_long = m1 * a_long*g * P.h_cg / P.L;      % N moved front->rear under accel
R.dW_lat  = m1 * a_lat*g  * P.h_cg / P.t_r;    % N, whole-vehicle lateral transfer
%      (splitting lateral transfer front/rear needs roll stiffness: next step)

%% 6. Rear-axle traction limit (ST-21)
% Rear-wheel drive only, at the limit: F = mu*(Wr_static + m*a*h/L) and F = m*a
a_max = P.mu * (Wr1/W1) / (1 - P.mu*P.h_cg/P.L);    % in g
Wr_dyn = Wr1 + m1*a_max*g*P.h_cg/P.L;
R.a_rear_only_max_g = a_max;
R.T_axle_rear_max   = P.mu * Wr_dyn * P.r_load;     % N*m at the rear axle (both wheels)

%% 7. Roll gradient (needs roll stiffness: placeholder)
R.roll_gradient = NaN;  % deg/g. Needs anti-roll bar rates and roll centres. [ST-21 stretch]

%% 8. Halfshaft angle through travel (ST-22)
z = linspace(P.travel(1), P.travel(2), 81);          % m, wheel travel from ride height
zt = P.z_offset0 - R.drop_rear + z;                  % joint height difference
R.shaft_travel = z;
R.shaft_angle_deg = atan2(zt, P.L_shaft) * 180/pi;
R.shaft_angle_max = max(abs(R.shaft_angle_deg));

if ~quiet, print_report(P, R, a_long, a_lat); end
end

% -------------------------------------------------------------------------
function check_inputs(P)
need = {'m_curb','L','t_r','wf','h_cg','k_s_r','MR_r','MRd_r','c_d_r','m_u_r','k_t', ...
        'r_load','mu','removed_rear','L_shaft','z_offset0','cv_limit_deg'};
missing = need(cellfun(@(f) any(isnan(P.(f))), need));
if any(isnan([P.added.m])) || any(isnan([P.added.x])), missing{end+1} = 'added.m / added.x'; end
if ~isempty(missing)
    error('susp_handcalcs:missing', ...
        'Set "%s" is missing: %s.\nFill these in susp_params.m (task ST-17), or run with ''example''.', ...
        P.set_name, strjoin(missing, ', '));
end
end

function print_report(P, R, a_long, a_lat)
fprintf('\n=== Suspension hand-calc check  [set: %s] ===\n', P.set_name);
if strcmpi(P.set_name, 'example')
    fprintf('*** TEACHING EXAMPLE: not Cherokee data. Do not report these numbers. ***\n');
end
fprintf('1  Added %.0f kg, net %.0f kg (allowance %.0f kg): %s\n', R.mass_added, R.mass_net, P.m_add_max, ...
        tf(R.within_allowance, 'within', 'OVER'));
fprintf('   Rear axle load %.0f -> %.0f N   rear share %.1f%% -> %.1f%%\n', R.Wr, 100*R.rear_fraction);
fprintf('2  Wheel rate %.1f N/mm, ride rate %.1f N/mm\n', R.wheel_rate/1e3, R.ride_rate/1e3);
fprintf('3  Rear static drop %.1f mm per corner\n', 1e3*R.drop_rear);
fprintf('4  Rear ride frequency %.2f -> %.2f Hz, damping ratio %.2f -> %.2f, wheel hop %.1f Hz\n', ...
        R.f_ride, R.zeta, R.f_wheelhop);
fprintf('5  Load transfer: %.0f N at %.2f g longitudinal, %.0f N at %.2f g lateral\n', ...
        R.dW_long, a_long, R.dW_lat, a_lat);
fprintf('6  Rear-only traction limit %.2f g, %.0f N*m at the rear axle (mu = %.2f)\n', ...
        R.a_rear_only_max_g, R.T_axle_rear_max, P.mu);
fprintf('7  Roll gradient: needs roll stiffness (not computed)\n');
fprintf('8  Max halfshaft angle %.1f deg over travel; joint limit %.1f deg: %s\n\n', ...
        R.shaft_angle_max, P.cv_limit_deg, tf(R.shaft_angle_max <= P.cv_limit_deg, 'OK', 'EXCEEDS'));
end

function s = tf(c, a, b)
if c, s = a; else, s = b; end
end

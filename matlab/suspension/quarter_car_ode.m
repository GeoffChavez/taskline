function Q = quarter_car_ode(set_name, which_rear)
%QUARTER_CAR_ODE  Quarter-car model solved with ode45 (no Simulink needed).
%
%   Q = quarter_car_ode('example')            converted vehicle, rear corner
%   Q = quarter_car_ode('example', 'stock')   stock rear corner
%
%   This is the reference answer for the Simulink model (ST-23): both should
%   give the same response to the same 20 mm road step. It reads the body
%   frequency and damping off the response and compares them with the hand
%   calculation, reporting percent error. The plot is the response to read by eye.
%
%   States: x = [zs; zs_dot; zu; zu_dot], measured from static equilibrium
%   (so gravity drops out). zr is the road input.
%       ms*zs'' = -Kw*(zs-zu) - cw*(zs'-zu')
%       mu*zu'' =  Kw*(zs-zu) + cw*(zs'-zu') - kt*(zu-zr)

if nargin < 1, set_name = 'example'; end
if nargin < 2, which_rear = 'converted'; end
H = susp_handcalcs(set_name, 0.4, 0.6, true);
P = susp_params(set_name);
k = strcmpi(which_rear, 'stock') * 1 + ~strcmpi(which_rear, 'stock') * 2;

ms = H.ms_corner(k);  mu = P.m_u_r;
Kw = H.wheel_rate;    kt = P.k_t;   cw = P.c_d_r * P.MRd_r^2;
step_h = 0.020;  t_step = 0.5;                       % 20 mm road step at 0.5 s
zr = @(t) step_h * (t >= t_step);
f  = @(t, x) [ x(2);
              (-Kw*(x(1)-x(3)) - cw*(x(2)-x(4))) / ms;
               x(4);
              ( Kw*(x(1)-x(3)) + cw*(x(2)-x(4)) - kt*(x(3)-zr(t))) / mu ];
opts = odeset('MaxStep', 1e-3, 'RelTol', 1e-7, 'AbsTol', 1e-9);
[t, x] = ode45(f, [0 4], zeros(4,1), opts);

% Model answer: damped modes from the eigenvalues of the state matrix.
% Each mode is lambda = -zeta*wn +/- j*wn*sqrt(1-zeta^2), so wn = |lambda| and
% zeta = -real(lambda)/|lambda|. The body mode is the slower one.
A = [ 0        1       0           0;
     -Kw/ms   -cw/ms   Kw/ms       cw/ms;
      0        0       0           1;
      Kw/mu    cw/mu  -(Kw+kt)/mu -cw/mu];
lam = eig(A);  lam = lam(imag(lam) > 0);
[~, order] = sort(abs(lam));  lam = lam(order);
fn   = abs(lam(1)) / (2*pi);   zeta = -real(lam(1)) / abs(lam(1));
Q.f_modes = abs(lam)' / (2*pi);
Q.t = t;  Q.zs = x(:,1);  Q.zu = x(:,3);
Q.f_body_measured = fn;  Q.zeta_measured = zeta;
Q.f_body_hand = H.f_ride(k);  Q.zeta_hand = H.zeta(k);
Q.err_f_pct    = 100 * (fn - Q.f_body_hand) / Q.f_body_hand;
Q.err_zeta_pct = 100 * (zeta - Q.zeta_hand) / Q.zeta_hand;

fprintf('Quarter car (%s rear, set %s), 20 mm step\n', which_rear, set_name);
fprintf('  Body frequency: hand %.2f Hz, model %.2f Hz, error %+.1f%%\n', Q.f_body_hand, fn, Q.err_f_pct);
fprintf('  Damping ratio : hand %.3f,  model %.3f,  error %+.1f%%\n', Q.zeta_hand, zeta, Q.err_zeta_pct);
fprintf('  Model modes: %.2f Hz (body), %.1f Hz (wheel hop)\n', Q.f_modes);
fprintf('  Error comes from the hand calc treating the wheel as fixed under the body\n');
fprintf('  (springs in series, unsprung mass not moving). Explaining it is the point.\n\n');

if usejava('jvm') || exist('OCTAVE_VERSION', 'builtin')
    try
        figure('Name', 'Quarter car step');
        plot(t, 1e3*x(:,1), t, 1e3*x(:,3), t, 1e3*zr(t), '--');
        xlabel('Time (s)'); ylabel('Displacement (mm)'); grid on;
        legend('Body z_s', 'Wheel z_u', 'Road z_r', 'Location', 'southeast');
        title(sprintf('Quarter car, %s rear (%s set)', which_rear, set_name));
    catch
    end
end
end

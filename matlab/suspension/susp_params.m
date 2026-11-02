function P = susp_params(set_name)
%SUSP_PARAMS  Inputs for the suspension hand calculations and models.
%
%   P = susp_params('cherokee')  Real vehicle. Published values are filled in;
%                                everything else is NaN with a [measure or
%                                confirm] note. Fill these in (task ST-17).
%   P = susp_params('example')   TEACHING EXAMPLE ONLY. Round numbers for a
%                                generic mid-size SUV so the scripts run while
%                                ST-17 is open. NOT Cherokee data. Never put an
%                                'example' result in a report or deliverable.
%
%   Units: SI throughout (kg, m, N, N/m, N*s/m, s). Spring rates are often
%   quoted in N/mm or lb/in: 1 N/mm = 1000 N/m, 1 lb/in = 175.13 N/m.
%
%   Motion ratio convention used everywhere in this folder:
%       MR = spring (or damper) travel / wheel travel     (usually < 1)
%       wheel rate  K_w = k_spring * MR^2
%   Some textbooks define MR the other way up. Check before copying numbers.

if nargin < 1, set_name = 'cherokee'; end
g = 9.81;
P = struct();
P.set_name = set_name;
P.g = g;

switch lower(set_name)
    case 'cherokee'
        % ---- Published (source in comment) ----------------------------------
        P.m_curb   = 1948;    % kg, Stellantis fleet guide. NOTE: constraints.json
                              % on the taskline says 1,972 kg. [confirm which]
        P.L        = 2.870;   % m, wheelbase, published 113.0 in
        P.t_r      = 1.633;   % m, rear track, published 64.3 in
        P.t_f      = 1.631;   % m, front track, published 64.2 in
        P.m_add_max = 182;    % kg, competition curb-weight allowance (+/-25 kg)

        % ---- Assumed: replace when measured ---------------------------------
        P.wf       = 0.57;    % front weight fraction, ASSUMED (~57/43). [measure: corner scales]

        % ---- Not published: ST-17 fills these -------------------------------
        P.h_cg     = NaN;     % m, CG height. [measure or confirm]
        P.k_s_r    = NaN;     % N/m, rear coil spring rate. [measure or confirm]
        P.MR_r     = NaN;     % rear spring motion ratio (spring/wheel). [measure]
        P.MRd_r    = NaN;     % rear damper motion ratio (damper/wheel). [measure]
        P.c_d_r    = NaN;     % N*s/m, rear damper coefficient at the damper. [confirm]
        P.m_u_r    = NaN;     % kg, rear unsprung mass per corner. [estimate + source]
        P.k_t      = NaN;     % N/m, tire vertical stiffness. [confirm: tire data]
        P.r_load   = 0.322;   % m, loaded tire radius, ASSUMED (team model value)
        P.mu       = NaN;     % tire-road friction coefficient for the traction case. [state it]

        % ---- Added components: name, mass (kg), x from FRONT axle (m) --------
        % Placeholder rows. Real masses come from the pack, EDM and mount designs.
        P.added = struct( ...
            'name', {'HV pack + enclosure', 'Rear drive unit (EDM)', 'Mounts, wiring, cooling'}, ...
            'm',    {NaN, NaN, NaN}, ...
            'x',    {NaN, NaN, NaN});
        P.removed_rear = NaN; % kg removed at the rear axle (stock rear driveline). [weigh it]

        % ---- Halfshaft geometry (ST-22) -------------------------------------
        P.L_shaft   = NaN;    % m, joint-to-joint halfshaft length. [measure in CAD]
        P.z_offset0 = NaN;    % m, wheel-joint height above drive-unit joint at stock ride height
        P.travel    = [-0.10 0.10]; % m, droop/bump range to plot. [confirm from service data]
        P.cv_limit_deg = NaN; % deg, CV joint angle limit. [joint datasheet]

    case 'example'
        warning('susp_params:example', ...
            'Using TEACHING EXAMPLE values. These are not Cherokee data.');
        P.m_curb = 2000;  P.L = 2.87;  P.t_r = 1.63;  P.t_f = 1.63;
        P.m_add_max = 182;
        P.wf    = 0.57;
        P.h_cg  = 0.70;
        P.k_s_r = 50e3;          % 50 N/mm
        P.MR_r  = 0.85;
        P.MRd_r = 0.85;
        P.c_d_r = 3500;
        P.m_u_r = 50;
        P.k_t   = 250e3;         % 250 N/mm
        P.r_load = 0.33;
        P.mu    = 0.8;
        P.added = struct( ...
            'name', {'HV pack + enclosure', 'Rear drive unit (EDM)', 'Mounts, wiring, cooling'}, ...
            'm',    {60, 100, 22}, ...
            'x',    {2.40, 2.95, 2.70});
        P.removed_rear = 0;
        P.L_shaft = 0.55;  P.z_offset0 = 0.02;  P.travel = [-0.10 0.10];
        P.cv_limit_deg = 20;     % example only: use your joint's datasheet

    otherwise
        error('susp_params:set', 'Unknown set "%s". Use ''cherokee'' or ''example''.', set_name);
end
end

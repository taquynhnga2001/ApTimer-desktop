# --------- SEQUENTIAL STEPS PERFORMED IN SETUP.m routine ---------
# 1. Defining file names to be read
# 2. Reading all 4 files and assigning variables
# 3. Unit conversion
# 4. Checking of data reading
# 5. Executing various Initial setups

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ====================== INTRODUCTION ==============================
print("                 Apatite F-Cl-OH diffusion")
print("____________________________________________________________")

# ---------- USER DEFINED PARAMETERS ----------
# Defining PARAMETERS
gamma = 0                    # 0-Lin., 1-Cyl., 2-Sph.
dx = 0.2                     # 'xstep' (in um)
dt0 = 10                     # 'tstep' (in seconds)
Intf_pos = 0                 # 'Intf_pos' (in um)
C_Mode = 1                   # Interpolation for initial composion
R_gas = 8.3144               # Universal gas constant (J/mol/K)
num_to1 = 1e-12              # Numerical tolerance limit
fname_meas = "Apa_Comp.txt"  # measured profile file: distance, Cl, F, OH (all molar yfractions)
# ____________________________________

# GEOMETRY of Domain; var.-'gamma'-0-Linear, 1-Cylindrical, 2-Spherical
if gamma == 0:
    geom = "Linear"
if gamma == 1:
    geom = "Cylindrical"
if gamma == 2:
    geom = "Spherical"


# ===================SET UP=======================
# -------------1. File names -----------------
fname_xC = 'initial_boundary.txt'
fname_tTPV = 'tTPV.txt'
fname_DC = 'Diffusion coeff.txt'
fname_BC = 'Boundary.txt'

# --------------2. Reading DIFFUSION COEFFICIENT data---------------
try:
    with open(fname_DC, 'r') as fid:
        fid_lines = fid.readlines()
        D0_L = []
        Ea_L = []
        Va_L = []
        D0_R = []
        Ea_R = []
        Va_R = []
        for lines in fid_lines[1:]:
            line = lines.strip().split("\t")
            # Storing the input data of Diffusion coeff. in list
            # for LHS medium
            D0_L.append(float(line[0]))    # in m2/sec
            Ea_L.append(float(line[1]))    # in J/mol
            Va_L.append(float(line[2]))    # in m3/mol
            # for RHS medium
            D0_R.append(float(line[3]))    # in m2/sec
            Ea_R.append(float(line[4]))    # in J/mol
            Va_R.append(float(line[5]))    # in m3/mol
    read_DC = 1
except:
    print("\n    >>ERROR: problem statement to go for profile setting")
    read_DC = 0

# ---------Reading Boundary & Interface conditions for each component ---------
try:
    with open(fname_BC, 'r') as fid:
        Bound_left = []
        F_left = []
        Bound_right = []
        F_right = []
        for lines in fid.readlines()[1:]:
            line = lines.strip().split('\t')
            # Storing the input data of Diffusion coeff. in lists
            Bound_left.append(float(line[0]))
            F_left.append(float(line[1]))
            Bound_right.append(float(line[2]))
            F_right.append(float(line[3]))
    read_BC = 1
except:
    print('\n    >>ERROR: problem in opening in Boundary cond. file')
    read_BC = 0

# --------Determining no. of components given by user--------
if len(D0_L) == len(D0_R) and len(D0_L) == len(Ea_R):
    if len(D0_R) == len(F_left) and len(D0_L) == len(Bound_right):
        component = len(D0_L)

# --------Reading INITIAL initial_boundary data----------
try:
    with open(fname_xC, 'r') as fid:
        line = fid.readlines()
        a = []
        conc_ii = np.zeros((2, component))    # array 2x3 (rows, cols)
        for k in range(2):
            a.append(float(line[k+1].split('\t')[0]))
            conc_ii[k, :] = np.array(line[k + 1].strip().split('\t')[1:])
            conc_i = conc_ii.transpose()      # array 3x2
    read_xc = 1     # conditional statement to go for profile
except:
    read_xc = 0

# ------ Reading time-Temperature-Interface velocity data -----
try:
    with open(fname_tTPV, 'r') as fid:
        time = []   # in years
        temp = []   # in Celsius
        for lines in fid.readlines()[1:]:
            line = lines.strip().split('\t')
            time.append(float(line[0]))
            temp.append(float(line[1]))
    read_tTPV = 1
except:
    print('\n      >>ERROR: problem in opening opening t-T-P-Intf_V file')

# ------------ Reading MEASURED PROFILE ---------------
try:
    with open(fname_meas, 'r') as fid:
        meas_dis = []
        lines = fid.readlines()
        meas_profile = np.zeros((3, len(lines)-1))     # array 3x19
        i = 0
        for line in lines[1:]:
            meas_dis.append(i)
            meas_profile[:, i] = np.array(line.strip().split('\t')[1:])
            i += 1
except:
    print('\n     >>ERROR: problem in reading parameters')

# ----------- CHECKING of reading status of files -----------
read_status = 0     # invalid reading
if read_DC == 1 and read_tTPV == 1:
    if read_xc == 1 and read_tTPV == 1:
        read_status = 1
        print(' Reading input files completed!')
# READING OF FILES ENDED

# -------------------3. Unit conversion ---------------------
if read_status == 1:
    # space variables in um// time in hours// Temp in Kelvin//
    # Energy in Joules

    # converting unit of D
    hr2sec = 60*60
    # converting D into um^2/hours
    D0_L = list(map(lambda x: x*(1e+12*hr2sec), D0_L))
    D0_R = list(map(lambda x: x*(1e+12*hr2sec), D0_R))
    # converting 'Celsius' to 'Kelvin'
    temp = list(map(lambda t: t + 273.15, temp))

    # Setting space gridding(s)
    # position of cell-walls
    xip = []
    a_i = a[0]
    count = 0
    while a_i <= a[1]:
        xip.append(a_i)
        count += 1
        a_i = a_i + dx

    # position of INTERFACE
    Intf_ind = xip.index(Intf_pos)
    # checking the position of Interfaces: xip[0] < Intf_ind < xip[end]
    if Intf_ind < 1:
        Intf_ind = 1
    if Intf_ind > len(xip)-1:
        Intf_ind = len(xip)-2
    Intf_ind0 = Intf_ind  # to store the initial interface pos.

    # position of cell-centers
    xcp = np.zeros((len(xip)-1))
    for k in range(len(xip)-1):
        xcp[k] = xip[k] + dx/2

    # checking space values for sph./cyl. geometry
    if gamma > 0:
        # setting the first element to zero value for sph./cyl/ geometry
        if xip[0] <= 0:
            # xip[0] = 0
            read_status = 0
            print('   >>Msg: Geometry is non-linear!')
            print("   >>     Don't give negative distance")
        if Intf_pos <= 0:
            # Intf_pos = xip[0]
            read_status = 0

if read_status == 1:
    # stroing in app. variables
    x = np.array(xcp)
    xnum = len(x)
    xsize = xip[-1] - xip[0]
    # total time-period for computtion
    t_length = time[-1] - time[0]

    # Setting initial concentration profile(s)
    # pre-allocating the vectors
    C_i = np.zeros((component, xnum))
    # setting initial profile
    if C_Mode == 1:
        # Flat homogeneous initial concentration in each medium
        for j in range(component):
            for i in range(xnum):
                if i < Intf_ind:
                    C_i[j, i] = conc_i[j, 0]
                elif i >= Intf_ind:
                    C_i[j, i] = conc_i[j, -1]
    else:
        # Linearly interpolated concentration for each component
        # interpolating at cell-faces
        C_inf = np.zeros((component, len(xip)))
        for k in range(component):
            for y in range(len(xip)):
                for i in range(1, len(a)):
                    if a[i-1] <= xip[y] <= a[i]:
                        cslope = (conc_i[k, i] - conc_i[k, i-1])/(a[i]-a[i-1])
                        cintercept = conc_i[k, i-1] - cslope*a[i-1]
                        C_inf[k, y] = cslope*xip[y] + cintercept
        # interpolating at cell-centres
        for l in range(component):
            for k in range(xnum):
                slope = (C_inf[l, k+1] - C_inf[l, k])/(xip[k+1] - xip[k])
                C_i[l, k] = slope*x[k] + C_inf[l, k] - slope*xip[k]

    # Total initial concentration for mass-balance check
    x_mb = np.array(x).reshape(len(x), 1)
    mass0 = np.zeros((component, 1))
    for kk in range(component):
        if kk == 0:
            for i in range(xnum):
                mass0[kk] += C_i[kk, i]*x_mb[i]**gamma*dx
        if kk == 1:
            for i in range(xnum):
                mass0[kk] += C_i[kk, i] * x_mb[i]**gamma*dx
        if kk == 2:
            for i in range(xnum):
                mass0[kk] += C_i[kk, i] * x_mb[i]**gamma*dx

    # Plotting initial profile and printing certain details
    C_plot = C_i.transpose()
    timesum = 0

    # import MC_PLOT
    print(' Solving for...\n')
    print(' MC Diffusion (', component, ' component)\n')
    print(' Space grid-size    : ', dx,' µm')
    print(' Number of grids    : ', xnum)
    print(' No. of Interf. Pos.: ', len(xip))
    print()
else:
    print('    >>ERR: Error in input files!')

# -------------------------------------------------------------------------------------
# forming handles for each component for plotting
err = {}
# forming string arrays for components' conc.
pq = Intf_ind     # for shortening the variable name
D_Cl = fid_lines[1].strip().split('\t')[0]
D_F = fid_lines[2].strip().split('\t')[0]
D_OH = fid_lines[3].strip().split('\t')[0]
xmax = 20

fig = make_subplots(rows=1, cols=3)

# PLOT fig 1. Cl
for kk in range(1):
    err[kk] = 0.02*meas_profile[kk, :]
    fig.add_trace(go.Scatter(x=meas_dis,
                             y=meas_profile[kk, :],
                             error_y=dict(array=err[kk], visible=True, color="black"),
                             mode="lines+markers",
                             name="Natural data Cl",
                             line=dict(color="black",dash="dash", width=2)),
                  row=1, col=1)
    if pq > 0:
        fig.add_trace(go.Scatter(x=[xip[0],]+ list(xcp[0:pq])+[xip[pq], xip[pq],]+list(xcp[pq:xnum])+ [xip[-1]],
                                 y=[C_plot[0, kk],]+ list(C_plot[0:pq, kk])+ [C_plot[pq-1,kk], C_plot[pq, kk]]+\
                                    list(C_plot[pq:xnum, kk]) + [C_plot[xnum-1, kk]],
                                 mode="lines",
                                 name='Model 1',
                                 line=dict(color='red')),
                      row=1, col=1)

    else:
        fig.add_trace(go.Scatter(x=xcp,
                                 y=C_plot[:, kk],
                                 mode="lines",
                                 name='Model 1',
                                 line=dict(color='red')),
                      row=1, col=1)

    fig.add_trace(go.Scatter(x=x-dx/2,
                             y=C_i[kk,:],
                             mode="lines",
                             line=dict(color='blue', dash='dash', width=1)),
                  row=1, col=1)

    fig.update_yaxes(title_text="X(Cl)", row=1, col=1, titlefont=dict(size=10), tickfont=dict(size=10))
    fig.update_xaxes(title_text="Distance (µm)", row=1, col=1, titlefont=dict(size=10), tickfont=dict(size=10))

    D_Cl_str = 'D(Cl) ='+str(D_Cl)+' m²/s'
    x_ano_1 = 3 * len(meas_dis) / 4
    y_ano_1 = 31 * meas_profile[kk][kk] / 32

    fig.add_trace(go.Scatter(x=[x_ano_1,],
                             y=[y_ano_1,],
                             mode="markers+text",
                             text=[D_Cl_str,],
                             textfont=dict(size=9),
                             line=dict(color="white"),
                             showlegend=False),
                  row=1, col=1)

# PLOT fig. 2 F
for kk in range(1, 2):
    err[kk] = 0.02*meas_profile[kk, :]
    fig.add_trace(go.Scatter(x=meas_dis,
                             y=meas_profile[kk, :],
                             error_y=dict(array=err[kk], visible=True, color="black"),
                             mode="lines+markers",
                             name="Natural data Cl",
                             line=dict(color="black",dash="dash", width=2)),
                  row=1, col=2)
    if pq > 0:
        fig.add_trace(go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                                 y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                   list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
                                 mode="lines",
                                 name='Model 2',
                                 line=dict(color='red')),
                      row=1, col=2)
    else:
        fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                 y=[C_plot[1,kk], C_plot[:,kk], C_plot[xnum,kk]],
                                 mode="lines",
                                 name='Model 2',
                                 line=dict(color='red')),
                      row=1, col=2)

    fig.add_trace(go.Scatter(x=x-dx/2,
                             y=C_i[kk,:],
                             mode="lines",
                             line=dict(color='blue', dash='dash', width=1)),
                  row=1, col=2)

    fig.update_yaxes(title_text="X(F)", row=1, col=2, titlefont=dict(size=10), tickfont=dict(size=10))
    fig.update_xaxes(title_text="Distance (µm)", row=1, col=2, titlefont=dict(size=10), tickfont=dict(size=10))

    D_Cl_str = 'D(F) ='+str(D_F)+' m²/s'
    x_ano_1 = 3 * len(meas_dis) / 4
    y_ano_1 = 31 * meas_profile[kk][kk] / 32

    fig.add_trace(go.Scatter(x=[x_ano_1, ],
                             y=[y_ano_1, ],
                             mode="markers+text",
                             text=[D_Cl_str, ],
                             textfont=dict(size=9),
                             line=dict(color="white"),
                             showlegend=False),
                  row=1, col=2)

# PLOT fig. 3 OH
for kk in range(2,3):
    err[kk] = 0.02*meas_profile[kk, :]
    fig.add_trace(go.Scatter(x=meas_dis,
                             y=meas_profile[kk, :],
                             error_y=dict(array=err[kk], visible=True, color="black"),
                             mode="lines+markers",
                             name="Natural data Cl",
                             line=dict(color="black", dash="dash", width=2)),
                  row=1, col=3)
    if pq > 0:
        fig.add_trace(go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                                 y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                   list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
                                 mode="lines",
                                 name='Model 3',
                                 line=dict(color='red')),
                      row=1, col=3)
    else:
        fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                 y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]],
                                 mode="lines",
                                 name='Model 3',
                                 line=dict(color='red')),
                      row=1, col=3)

    fig.add_trace(go.Scatter(x=x-dx/2,
                             y=C_i[kk, :],
                             mode="lines",
                             line=dict(color='blue', dash='dash', width=1)),
                  row=1, col=3)

    fig.update_yaxes(title_text="X(OH)", row=1, col=3, titlefont=dict(size=10), tickfont=dict(size=10))
    fig.update_xaxes(title_text="Distance (µm)", row=1, col=3, titlefont=dict(size=10), tickfont=dict(size=10))

    D_Cl_str = 'D(OH) ='+str(D_OH)+' m²/s'
    x_ano_1 = 3 * len(meas_dis) / 4
    y_ano_1 = 31 * meas_profile[kk][kk] / 32

    fig.add_trace(go.Scatter(x=[x_ano_1,],
                             y=[y_ano_1,],
                             mode="markers+text",
                             text=[D_Cl_str,],
                             textfont=dict(size=9),
                             line=dict(color="white"),
                             showlegend=False),
                  row=1, col=3)

    fig['layout'].update(width=1230, height=400, autosize=False)
    fig.update_layout(showlegend=False)
    fig.write_image("images/Row1.png")
    # fig.show()
# --------------- FINISH PLOTTING ROW 1 -----------------


# =================== MAIN CALCULATION =========================
print(' Computation starts..!\n\n')
# variables storing evolution of parameters
C_f = np.zeros((component, xnum))     # final concentration matrix
time_evo = []
T_evo = []
time_evo.append(0)                       # time evolution record
T_evo.append(temp[0])                    # Temp evolution record

# converting 'phi=' from row to column vector so as to match
# with dimensions of 'phin' for ease of programming
# size (phi0/phin) = matrix (xnum, component)
phi0 = C_i.transpose()
phin = np.zeros((len(phi0), len(phi0[0])))
timesum = 0     # total real time elapsed
t = 0           # iteration/time-step index

# Main Computation starts
while timesum < t_length:
    t = t+1         # increasing the iteration index
    if t % 50 == 0:
        print('     ... {} iteration ... \n'.format(t))
    # Calculating Temperature
    for i in range(1, len(time)):
        if (time[i-1]-num_to1) <= timesum <= (time[i]+num_to1):
            Tslope = (temp[i] - temp[i-1])/(time[i]-time[i-1])
            Tintercept = temp[i-1] - (Tslope*time[i-1])
            T_rock = Tslope*timesum + Tintercept

    # Calculating the TIME-STEP (dt)
    dt = min(dt0, t_length-timesum)    # given time-step is dt0

    # Tracer_D as f(Pressure-Temperature)
    DLft = np.zeros((component, 1))
    DRgt = np.zeros((component, 1))
    for kl in range(0, component):
        DLft[kl] = D0_L[kl]
        DRgt[kl] = D0_R[kl]

    # Tracer_D as f(composition)
    # creating Tracer_D vector of each component at each cell
    # centers to account for compositional dependence of D*
    # calculating # at each cell-centre acc. to composition
    D_xcp = np.zeros((component, xnum))
    for l in range(0, component):
        for j in range(0, len(x)):
            if j <= Intf_ind - 1:
                D_xcp[l, j] = DLft[l]
            else:
                D_xcp[l, j] = DRgt[l]

    # CALCULATION FOR NUMERICAL SOLUTION BEGINS
    for gg in range(component-1):

        # MC_D-coeff terms for appro. component from D_matrix
        # calculating terms from D_matrix for a component

        # D11     D12     D13     D14  .... D1(n-1)
        # D21     D22     D23     D24  .... D2(n-1)
        # ...
        # D(n-1)1 D(n-1)2 D(n-1)3 D(n-1)4 . D(n-1)(n-1)

        # e.g for component 1; D11, D12, D13, ..., D1(n-1) will be calculated at
        # new time step, i.e. implicit time
        # component index should be used to identify the component

        MC_D = np.zeros((component -1, xnum))
        for i in range(0, xnum):
            sig_DX = 0
            for k in range(0, component):
                sig_DX = sig_DX + D_xcp[k, i]*phi0[i, k]
            for hh in range(0, component-1):
                # Kronecker delta
                Kro_del = 0
                if gg == hh:
                    Kro_del = 1
                term1 = D_xcp[gg, i]*Kro_del
                term2 = ((D_xcp[gg, i]*phi0[i, gg])/sig_DX)*(D_xcp[hh, i]-D_xcp[component-1, i])
                # by default last component will be taken as dependent component
                MC_D[hh, i] = term1 - term2

        # interpolating D at cell-interfaces from surrounding cell-centres
        D_xip_0 = np.zeros((component-1, len(xip)))
        for m in range(0, component-1):
            for j in range(1, len(xip)-1):
                D_xip_0[m, j] = (2*MC_D[m, j-1]*MC_D[m, j])/(MC_D[m, j-1] + MC_D[m, j])
                # putting the immediate next D values for domain boundaries
                D_xip_0[m, 0] = D_xip_0[m, 1]
                D_xip_0[m, -1] = D_xip_0[m, xnum-1]

        # storing D_xip_0 into the working variable
        D_xip = D_xip_0

        # Assigning boundary, flux & interface cond. for each component
        BC_left = Bound_left[gg]
        flux_left = F_left[gg]
        BC_right = Bound_right[gg]
        flux_right = F_right[gg]

        # Numerical solution
        L = np.zeros((xnum, xnum))      # matrix of the coefficients
        R = np.zeros((xnum, 1))         # right hand side vector
        # Space Loop starts
        for i in range(0, xnum):
            # Defining the boundaries by FVM EQUATIONS
            if i == 0:            # LEFT BOUNDARY CONDITION
                if BC_left == 1:        # fixed concentration
                    A3 = 0
                    rRri = 0
                    off_D_term = 0
                elif BC_left == 2:     # zero flux
                    # diagonal D_terms for L Matrix
                    Dr = D_xip[gg, i+1]
                    A3 = Dr*dt/dx**2
                    rRri = ((x[i] + 0.5*dx)/x[i])**gamma

                    # off diagonal D_terms for RHS coefficients
                    off_D_term = 0
                    for hh in range(0, component-1):
                        if hh == gg:
                            off_D_term = 0
                        else:
                            B3 = D_xip[hh, i+1]*dt/dx**2
                            # adding all off-diagonal terms
                            off_D_term = off_D_term + ((B3*rRri*phi0[i+1, hh])-(B3*rRri*phi0[i, hh]))
                # MATRIX
                L[i, i] = 1+(A3*rRri)
                L[i, i+1] = -A3*rRri
                # RHS coefficients
                R[i, 0] = phi0[i, gg] + off_D_term

            elif i == xnum-1:         # RIGHT BOUNDARY CONDITION
                if BC_right == 1:     # fixed concentration
                    A1 = 0
                    rLri = 0
                    off_D_term = 0
                elif BC_right == 2:   # zero flux
                    # diagonal D_terms for L Matrix
                    Dl = D_xip[gg, i]
                    A1 = Dl*dt/dx**2
                    rLri = ((x[i]-0.5*dx)/x[i])*gamma

                    # off diagonal D_terms for RHS coefficients
                    off_D_term = 0
                    for hh in range(0, component-1):
                        if hh == gg:
                            off_D_term = 0
                        else:
                            B1 = D_xip[hh, i]*dt/dx**2
                            # adding all off-diagonal terms
                            off_D_term = off_D_term * ((B1*rLri*phi0[i-1, hh])-(B1*rLri*phi0[i, hh]))

                # MATRIX
                L[i, i-1] = -A1*rLri
                L[i, i] = 1 + (A1*rLri)
                # RHS coefficients
                R[i, 0] = phi0[i, gg] + off_D_term

            else:      # INTERNAL NODES
                # diagonal D_terms
                Dl = D_xip[gg, i]
                Dr = D_xip[gg, i+1]
                A1 = Dl*dt/dx**2
                A3 = Dr*dt/dx**2
                # radius_terms
                rLri = ((x[i]-0.5*dx)/x[i])**gamma
                rRri = ((x[i]+0.5*dx)/x[i])**gamma

                # MATRIX coefficients
                L[i, i-1] = -A1*rLri
                L[i, i] = 1 + (A1*rLri) + (A3*rRri)
                L[i, i+1] = -A3*rRri

                # RHS VECTOR
                # off diagonal D_terms
                off_D_term = 0
                for hh in range(0, component-1):
                    if hh == gg:
                        off_D_term = 0
                    else:
                        B1 = D_xip[hh, i] * dt/dx**2
                        B3 = D_xip[hh, i+1]*dt/dx**2
                        # adding all off-diagonal terms
                        off_D_term = off_D_term *\
                                     ((B1*rLri*phi0[i-1, hh])-
                                      ((B1*rLri+B3*rRri)*phi0[i, hh])+
                                      (B3*rRri*phi0[i+1, hh]))
                R[i, 0] = phi0[i, gg] + off_D_term

        # SPACE LOOP ENDS

        # computing the matrix
        phin[:, gg] = list(np.matmul(np.linalg.inv(L), R))

        # calculating the concentration of the dependent component
    for i in range(xnum):
        sum_IndComp = 0
        for hh in range(component-1):
            sum_IndComp = sum_IndComp + phin[i, hh]
        phin[i, -1] = 1.0 - sum_IndComp
    # saving to initial profile
    phi0 = phin

    # plotting
    C_plot = phin
    # ------------------- START PLOTTING ------------------------
    # PLOT fig 1. Cl
    for kk in range(1):
        err[kk] = 0.02 * meas_profile[kk, :]
        fig.add_trace(go.Scatter(x=meas_dis,
                                 y=meas_profile[kk, :],
                                 error_y=dict(array=err[kk], visible=True, color="black"),
                                 mode="lines+markers",
                                 name="Natural data Cl",
                                 line=dict(color="black", dash="dash", width=2)),
                      row=1, col=1)
        if pq > 0:
            # fig.add_trace(
            #     go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
            #                y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
            #                  list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
            #                mode="lines",
            #                line=dict(color='red')),
            #     row=1, col=1)
            fig.update_traces(go.Scatter(
                x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                             list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]),
                              selector=dict(name='Model 1'))

        else:
            # fig.add_trace(go.Scatter(x=xcp,
            #                          y=C_plot[:, kk],
            #                          mode="lines",
            #                          line=dict(color='red')),
            #               row=1, col=1)
            fig.update_traces(go.Scatter(x=xcp, y=C_plot[:, kk]), selector=dict(name='Model 1'))

        fig.add_trace(go.Scatter(x=x - dx / 2,
                                 y=C_i[kk, :],
                                 mode="lines",
                                 line=dict(color='blue', dash='dash', width=1)),
                      row=1, col=1)

        fig.update_yaxes(title_text="X(Cl)", row=1, col=1, titlefont=dict(size=10), tickfont=dict(size=10))
        fig.update_xaxes(title_text="Distance (µm)", row=1, col=1, titlefont=dict(size=10), tickfont=dict(size=10))

        D_Cl_str = 'D(Cl) =' + str(D_Cl) + ' m²/s'
        x_ano_1 = 3 * len(meas_dis) / 4
        y_ano_1 = 31 * meas_profile[kk][kk] / 32

        fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                 y=[y_ano_1, ],
                                 mode="markers+text",
                                 text=[D_Cl_str, ],
                                 textfont=dict(size=9),
                                 line=dict(color="white"),
                                 showlegend=False),
                      row=1, col=1)

    # PLOT fig. 2 F
    for kk in range(1, 2):
        err[kk] = 0.02 * meas_profile[kk, :]
        fig.add_trace(go.Scatter(x=meas_dis,
                                 y=meas_profile[kk, :],
                                 error_y=dict(array=err[kk], visible=True, color="black"),
                                 mode="lines+markers",
                                 name="Natural data Cl",
                                 line=dict(color="black", dash="dash", width=2)),
                      row=1, col=2)
        if pq > 0:
            # fig.add_trace(
            #     go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
            #                y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
            #                  list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
            #                mode="lines",
            #                line=dict(color='red')),
            #     row=1, col=2)
            fig.update_traces(go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                           y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                             list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]), selector=dict(name='Model 2'))

        else:
            # fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
            #                          y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]],
            #                          mode="lines",
            #                          line=dict(color='red')),
            #               row=1, col=2)
            fig.update_traces(
                go.Scatter(x=[xip[0], xcp, xip[-1]], y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]),
                           selector=dict(name='Model 2'))

        fig.add_trace(go.Scatter(x=x - dx / 2,
                                 y=C_i[kk, :],
                                 mode="lines",
                                 line=dict(color='blue', dash='dash', width=1)),
                      row=1, col=2)

        fig.update_yaxes(title_text="X(F)", row=1, col=2, titlefont=dict(size=10), tickfont=dict(size=10))
        fig.update_xaxes(title_text="Distance (µm)", row=1, col=2, titlefont=dict(size=10), tickfont=dict(size=10))

        D_F_str = 'D(F) =' + str(D_F) + ' m²/s'
        x_ano_1 = 3 * len(meas_dis) / 4
        y_ano_1 = 31 * meas_profile[kk][kk] / 32

        fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                 y=[y_ano_1, ],
                                 mode="markers+text",
                                 text=[D_F_str, ],
                                 textfont=dict(size=9),
                                 line=dict(color="white"),
                                 showlegend=False),
                      row=1, col=2)

    # PLOT fig. 3 OH
    for kk in range(2, 3):
        err[kk] = 0.02 * meas_profile[kk, :]
        fig.add_trace(go.Scatter(x=meas_dis,
                                 y=meas_profile[kk, :],
                                 error_y=dict(array=err[kk], visible=True, color="black"),
                                 mode="lines+markers",
                                 name="Natural data Cl",
                                 line=dict(color="black", dash="dash", width=2)),
                      row=1, col=3)
        if pq > 0:
            # fig.add_trace(
            #     go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
            #                y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
            #                  list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
            #                mode="lines",
            #                line=dict(color='red')),
            #     row=1, col=3)
            fig.update_traces(go.Scatter(
                x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                             list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]), selector=dict(name='Model 3'))
        else:
            # fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
            #                          y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]],
            #                          mode="lines",
            #                          line=dict(color='red')),
            #               row=1, col=3)
            fig.update_traces(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                     y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]), selector=dict(name='Model 3'))

        fig.add_trace(go.Scatter(x=x - dx / 2,
                                 y=C_i[kk, :],
                                 mode="lines",
                                 line=dict(color='blue', dash='dash', width=1)),
                      row=1, col=3)

        fig.update_yaxes(title_text="X(OH)", row=1, col=3, titlefont=dict(size=10), tickfont=dict(size=10))
        fig.update_xaxes(title_text="Distance (µm)", row=1, col=3, titlefont=dict(size=10), tickfont=dict(size=10))

        D_OH_str = 'D(OH) =' + str(D_OH) + ' m²/s'
        x_ano_1 = 3 * len(meas_dis) / 4
        y_ano_1 = 31 * meas_profile[kk][kk] / 32

        fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                 y=[y_ano_1, ],
                                 mode="markers+text",
                                 text=[D_OH_str, ],
                                 textfont=dict(size=9),
                                 line=dict(color="white"),
                                 showlegend=False),
                      row=1, col=3)

        fig['layout'].update(width=1230, height=400, autosize=False)
        fig.update_layout(showlegend=False)
        fig.write_image("images/plot.png")
        fig.write_image("images/Row2.png")
        # FINISH PLOTTING...................
    # update iterator
    timesum = timesum + dt
    time_evo.append(timesum)
    T_evo.append(T_rock)

print('Computation ends!')

# Storing the last profile & Mass-balance check ------------------------
C_f = np.transpose(phin)

# mass-balance check
massf = np.zeros((1, component))
mass_error = np.zeros((1, component))
Hesse_error = np.zeros((1, component))

for kk in range(component):
    massf[0, kk] = np.matmul(x**gamma, phin[:, kk]*dx)
    Hesse_error[0, kk] = abs(massf[0, kk] - mass0[kk, 0])/xnum
    mass_error[0, kk] = (abs(massf[0, kk] - mass0[kk, 0])/mass0[kk, 0])*1e2

print(' Total No. of iterations: ', t-1)
print(' Total time lapsed (hrs): ', timesum)
print()
print('Mass balance...')
print(' Component \tError[%]\t\t\tError[Hesse]')
for kk in range(component):
    print(' ', kk, '\t', mass_error[0, kk], '\t\t', Hesse_error[0, kk])

print()
print('Program finished!')

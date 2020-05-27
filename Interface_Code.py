import wx
import wx.lib.scrolledpanel
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from scipy.interpolate import interp1d


class Frame(wx.Frame):
    def __init__(self, parent, title):
        super(Frame, self).__init__(parent, title=title, size=(1300, 800))
        self.SetIcon(wx.Icon("images/icon.jpg", wx.BITMAP_TYPE_ANY))

        self.mainpanel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, style=wx.SIMPLE_BORDER, size=(1300, 1000))
        self.mainpanel.SetupScrolling()

        programsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        heading_sizer = wx.BoxSizer(wx.HORIZONTAL)
        heading_sizer_main = wx.BoxSizer(wx.VERTICAL)
        instruction_sizer = wx.BoxSizer(wx.VERTICAL)
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        model_sizer = wx.BoxSizer(wx.VERTICAL)

        # ================================ HEADING ==============================================
        heading = wx.StaticText(self.mainpanel, label="ApTimer:", pos=(170, 15))
        font18 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading.SetFont(font18)
        heading.SetForegroundColour('red')
        heading_sizer.Add(heading, 0, wx.LEFT | wx.ALIGN_CENTER, 200)
        # Text: content of ApTimer
        content_txt = 'timescales of magma ascent modelled using F-Cl-OH diffusion in apatite'
        content = wx.StaticText(self.mainpanel, label=content_txt, pos=(290, 18))
        font16 = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        content.SetFont(font16)
        heading_sizer.Add(content, 0, wx.ALL, 13)
        heading_sizer_main.Add(heading_sizer, 0, wx.ALL, 0)

        # ==================================== INSTRUCTION BOX ===================================
        # Text: Instruction
        instruction = wx.StaticText(self.mainpanel, label='Instruction:', pos=(20, 70))
        font12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        instruction.SetFont(font12)
        instruction_sizer.Add(instruction, 0, wx.ALL, 10)
        # Text: purpose
        purpose_txt1 = "This model aims to calculate the timescales of F-Cl-OH diffusion in apatite. Diffusivity were \
determined from experiments at 800-1100°C 1-atm by the authors below:"
        purpose1 = wx.StaticText(self.mainpanel, label=purpose_txt1, pos=(20, 100))
        font12light = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        purpose1.SetFont(font12light)
        instruction_sizer.Add(purpose1, 0, wx.ALL, 10)
        # Text: authors
        authors_txt = "Li W., Chakraborty S., Nagashima K. and Costa F. (2020) Multicomponent diffusion of F-Cl-OH in \
apatite with application to determining magma ascent rates. (DOI: ...)"
        authors = wx.StaticText(self.mainpanel, label=authors_txt, pos=(20, 155))
        authors.SetFont(font12light)
        instruction_sizer.Add(authors, 0, wx.ALL, 10)

        # =============================== INPUT BOX =========================================
        # Text: Input
        font11 = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font11light = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        font10light = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        Input = wx.StaticText(self.mainpanel, label='Input:', pos=(20, 210))
        font14 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        Input.SetFont(font14)
        Input.SetForegroundColour('red')
        input_sizer.Add(Input, 0, wx.ALL, 20)
        # -------------------- Text: Diffusion profiles: ------------------------------
        input_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        diff_profile = wx.StaticText(self.mainpanel, label='Diffusion profiles:', pos=(30, 240))
        diff_profile.SetFont(font11)
        input_sizer1.Add(diff_profile, 0, wx.LEFT, 20)
        please_use_txt = '*Please use the provided template (.csv) to organize your data, and upload them using the blue \
button below.'
        please_use = wx.StaticText(self.mainpanel, label=please_use_txt, pos=(170, 241))
        please_use.SetFont(font10light)
        input_sizer1.Add(please_use, 0, wx.LEFT, 20)
        input_sizer.Add(input_sizer1)
        # Data template button
        input_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        data_template = wx.Button(self.mainpanel, label='Data Template', pos=(30, 260), size=(120, 30))
        data_template.Bind(wx.EVT_BUTTON, self.OnDataTemplate)
        data_template.SetFont(font11)
        data_template.SetBackgroundColour('slate BLUE')
        data_template.SetForegroundColour('white')
        input_sizer2.Add(data_template, 0, wx.LEFT, 20)
        # Upload data button
        upload_data = wx.Button(self.mainpanel, label='Upload Data', pos=(180, 260), size=(120, 30))
        upload_data.Bind(wx.EVT_BUTTON, self.OnUpload)
        upload_data.SetFont(font11)
        upload_data.SetBackgroundColour('sky blue')
        upload_data.SetForegroundColour('white')
        input_sizer2.Add(upload_data, 0, wx.LEFT, 50)
        # Plot data button
        plot_data = wx.Button(self.mainpanel, label='Plot Data', pos=(330, 260), size=(120, 30))
        plot_data.Bind(wx.EVT_BUTTON, self.OnPlotData)
        plot_data.SetFont(font11)
        plot_data.SetBackgroundColour('steel blue')
        plot_data.SetForegroundColour('white')
        input_sizer2.Add(plot_data, 0, wx.LEFT, 50)
        input_sizer.Add(input_sizer2)
        # ----------------------- PLOT IMAGE -----------------------------------------
        self.figure_pic1 = wx.StaticBitmap(self.mainpanel, pos=(30, 295))
        self.figure_pic1.SetBitmap(wx.Bitmap('images/Blank.png'))
        self.plot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.plot_sizer.Add(self.figure_pic1)
        input_sizer.Add(self.plot_sizer, 0, wx.ALL, 20)

        colData = wx.BoxSizer(wx.HORIZONTAL)
        col1 = wx.BoxSizer(wx.VERTICAL)
        col2 = wx.BoxSizer(wx.VERTICAL)
        col3 = wx.BoxSizer(wx.VERTICAL)
        # ----------------------- Parameters used for modeling -----------------------
        parameter = wx.StaticText(self.mainpanel, label='Parameters used for diffusion modeling:', pos=(50, 350))
        parameter.SetFont(font11)
        col1.Add(parameter, 0, wx.LEFT, 20)
        col1hor = wx.BoxSizer(wx.HORIZONTAL)
        col1hor_1 = wx.BoxSizer(wx.VERTICAL)
        col1hor_2 = wx.BoxSizer(wx.VERTICAL)
        col1hor_3 = wx.BoxSizer(wx.VERTICAL)
        # Temperature
        temperature = wx.StaticText(self.mainpanel, label='Temperature:', pos=(65, 375))
        temperature.SetFont(font11light)
        self.temp_input = wx.TextCtrl(self.mainpanel, pos=(280, 373), size=(70, 20))  # input field
        self.temp_input.SetFont(font11light)
        self.temp_input.SetValue('900')
        temp_unit = wx.StaticText(self.mainpanel, label='°C', pos=(360, 375))
        temp_unit.SetFont(font11light)
        col1hor_1.Add(temperature, 0, wx.TOP, 10)
        col1hor_2.Add(self.temp_input)
        col1hor_3.Add(temp_unit, 0, wx.TOP, 0)
        # Tilt of traverse
        tilt = wx.StaticText(self.mainpanel, label='Tilt of traverse from the c-axis:')
        tilt.SetFont(font11light)
        self.tilt_input = wx.TextCtrl(self.mainpanel, size=(70, 20))
        self.tilt_input.SetFont(font11light)
        self.tilt_input.SetValue('17')
        tilt_unit = wx.StaticText(self.mainpanel, label='degree')
        tilt_unit.SetFont(font11light)
        col1hor_1.Add(tilt, 0, wx.TOP, 10)
        col1hor_2.Add(self.tilt_input, 0, wx.TOP, 5)
        col1hor_3.Add(tilt_unit, 0, wx.TOP, 10)
        # D(F) D(Cl) D(OH)
        col1hor_11 = wx.BoxSizer(wx.HORIZONTAL)
        col1hor_1col = wx.BoxSizer(wx.VERTICAL)
        DCl = wx.StaticText(self.mainpanel, label='D(Cl)', pos=(230, 430))
        DCl.SetFont(font11)
        col1hor_1col.Add(DCl, 0, wx.TOP, 2)
        self.DCl_input = wx.TextCtrl(self.mainpanel, pos=(280, 428), size=(70, 20), style=wx.TE_READONLY)
        self.DCl_input.SetFont(font11light)  # ________________________
        col1hor_2.Add(self.DCl_input, 0, wx.TOP, 5)
        DF = wx.StaticText(self.mainpanel, label='D(F)', pos=(230, 455))
        DF.SetFont(font11)
        col1hor_1col.Add(DF, 0, wx.TOP, 6)
        self.DF_input = wx.TextCtrl(self.mainpanel, pos=(280, 453), size=(70, 20), style=wx.TE_READONLY)
        self.DF_input.SetFont(font11light)  # ________________________
        col1hor_2.Add(self.DF_input, 0, wx.TOP, 5)
        DOH = wx.StaticText(self.mainpanel, label='D(OH)', pos=(230, 480))
        DOH.SetFont(font11)
        col1hor_1col.Add(DOH, 0, wx.TOP, 6)
        self.DOH_input = wx.TextCtrl(self.mainpanel, pos=(280, 478), size=(70, 20), style=wx.TE_READONLY)
        self.DOH_input.SetFont(font11light)  # ________________________
        col1hor_2.Add(self.DOH_input, 0, wx.TOP, 5)
        D_unit1 = wx.StaticText(self.mainpanel, label='m²/s', pos=(360, 430))
        D_unit2 = wx.StaticText(self.mainpanel, label='m²/s', pos=(360, 455))
        D_unit3 = wx.StaticText(self.mainpanel, label='m²/s', pos=(360, 480))
        D_unit1.SetFont(font11light)
        D_unit2.SetFont(font11light)
        D_unit3.SetFont(font11light)
        col1hor_3.Add(D_unit1, 0, wx.TOP, 8)
        col1hor_3.Add(D_unit2, 0, wx.TOP, 8)
        col1hor_3.Add(D_unit3, 0, wx.TOP, 8)
        # Calculate diffusivity button
        calculate_diff = wx.Button(self.mainpanel, label='Calculate\ndiffusivity', pos=(65, 430), size=(150, 70))
        calculate_diff.SetFont(font11)
        calculate_diff.SetBackgroundColour('sea green')
        calculate_diff.SetForegroundColour('white')
        calculate_diff.Bind(wx.EVT_BUTTON, self.OnCalculateDiff)
        col1hor_11.Add(calculate_diff, 0, wx.TOP, 5)
        col1hor_11.Add(col1hor_1col, 0, wx.TOP | wx.LEFT, 5)
        col1hor_1.Add(col1hor_11)
        col1hor.Add(col1hor_1, 0, wx.LEFT, 20)
        col1hor.Add(col1hor_2, 0, wx.LEFT | wx.TOP, 10)
        col1hor.Add(col1hor_3, 0, wx.LEFT | wx.TOP, 10)
        col1.Add(col1hor)
        colData.Add(col1)
        # -------------------- Initial conditions and Boundaries -----------------------
        ini_text_bold = wx.StaticText(self.mainpanel, label="Initial && Boundary conditions:", pos=(450, 650))
        ini_text_bold.SetFont(font11)
        col2.Add(ini_text_bold)
        col2hor = wx.BoxSizer(wx.HORIZONTAL)
        col2hor_1 = wx.BoxSizer(wx.VERTICAL)
        col2hor_2 = wx.BoxSizer(wx.VERTICAL)
        col2hor_3 = wx.BoxSizer(wx.VERTICAL)
        col2hor_4 = wx.BoxSizer(wx.VERTICAL)
        XCl_text = wx.StaticText(self.mainpanel, label="X(Cl)", pos=(65, 555))
        XCl_text.SetFont(font11)
        col2hor_1.Add(XCl_text, 0, wx.TOP, 48)
        XF_text = wx.StaticText(self.mainpanel, label="X(F)", pos=(65, 580))
        XF_text.SetFont(font11)
        col2hor_1.Add(XF_text, 0, wx.TOP, 5)
        XOH_text = wx.StaticText(self.mainpanel, label="X(OH)", pos=(65, 605))
        XOH_text.SetFont(font11)
        col2hor_1.Add(XOH_text, 0, wx.TOP, 5)
        col2hor.Add(col2hor_1)
        ini_text = wx.StaticText(self.mainpanel, label="Initial\nconditions:", pos=(120, 515))
        ini_text.SetFont(font11light)
        col2hor_2.Add(ini_text, 0, wx.TOP, 5)
        self.XCl_ini_input = wx.TextCtrl(self.mainpanel, pos=(120, 555), size=(70, 20))
        self.XF_ini_input = wx.TextCtrl(self.mainpanel, pos=(120, 580), size=(70, 20))
        self.XOH_ini_input = wx.TextCtrl(self.mainpanel, pos=(120, 605), size=(70, 20))
        self.XCl_ini_input.SetFont(font11light)
        self.XF_ini_input.SetFont(font11light)
        self.XOH_ini_input.SetFont(font11light)
        left_text = wx.StaticText(self.mainpanel, label="Left\nboundary:", pos=(230, 515))
        left_text.SetFont(font11light)
        col2hor_3.Add(left_text, 0, wx.TOP, 5)
        self.XCl_left_input = wx.TextCtrl(self.mainpanel, pos=(230, 555), size=(70, 20))
        self.XF_left_input = wx.TextCtrl(self.mainpanel, pos=(230, 580), size=(70, 20))
        self.XOH_left_input = wx.TextCtrl(self.mainpanel, pos=(230, 605), size=(70, 20))
        self.XCl_left_input.SetFont(font11light)
        self.XF_left_input.SetFont(font11light)
        self.XOH_left_input.SetFont(font11light)
        right_text = wx.StaticText(self.mainpanel, label="Right\nboundary:", pos=(340, 515))
        right_text.SetFont(font11light)
        col2hor_4.Add(right_text, 0, wx.TOP, 5)
        self.XCl_right_input = wx.TextCtrl(self.mainpanel, pos=(340, 555), size=(70, 20))
        self.XF_right_input = wx.TextCtrl(self.mainpanel, pos=(340, 580), size=(70, 20))
        self.XOH_right_input = wx.TextCtrl(self.mainpanel, pos=(340, 605), size=(70, 20))
        self.XCl_right_input.SetFont(font11light)
        self.XF_right_input.SetFont(font11light)
        self.XOH_right_input.SetFont(font11light)
        plot_button = wx.Button(self.mainpanel, size=(125, 35), label="Plot")
        plot_button.SetFont(font11)
        plot_button.SetBackgroundColour('sea green')
        plot_button.SetForegroundColour('white')
        plot_button.Bind(wx.EVT_BUTTON, self.OnPlot)
        col2hor_2.Add(self.XCl_ini_input, 0, wx.TOP, 5)
        col2hor_2.Add(self.XF_ini_input, 0, wx.TOP, 5)
        col2hor_2.Add(self.XOH_ini_input, 0, wx.TOP, 5)
        col2hor_3.Add(self.XCl_left_input, 0, wx.TOP, 5)
        col2hor_3.Add(self.XF_left_input, 0, wx.TOP, 5)
        col2hor_3.Add(self.XOH_left_input, 0, wx.TOP, 5)
        col2hor_4.Add(self.XCl_right_input, 0, wx.TOP, 5)
        col2hor_4.Add(self.XF_right_input, 0, wx.TOP, 5)
        col2hor_4.Add(self.XOH_right_input, 0, wx.TOP, 5)
        col2hor.Add(col2hor_2, 0, wx.LEFT, 10)
        col2hor.Add(col2hor_3, 0, wx.LEFT, 20)
        col2hor.Add(col2hor_4, 0, wx.LEFT, 20)
        col2.Add(col2hor)
        col2.Add(plot_button, 0, wx.TOP, 5)
        colData.Add(col2, 0, wx.LEFT, 100)
        # set values as previous values
        try:
            with open('previousIniBound.txt', 'r') as prevFile:
                lines = prevFile.readlines()
                Cl = lines[0].strip().split(',')
                F = lines[1].strip().split(',')
                OH = lines[2].strip().split(',')
                self.XCl_ini_input.SetValue(Cl[0])
                self.XCl_left_input.SetValue(Cl[1])
                self.XCl_right_input.SetValue(Cl[2])
                self.XF_ini_input.SetValue(F[0])
                self.XF_left_input.SetValue(F[1])
                self.XF_right_input.SetValue(F[2])
                self.XOH_ini_input.SetValue(OH[0])
                self.XOH_left_input.SetValue(OH[1])
                self.XOH_right_input.SetValue(OH[2])
        except FileNotFoundError:
            pass
        # ----------------------- Last steps and run -----------------------------------
        dis_step = wx.StaticText(self.mainpanel, label="Distance && Time steps:", pos=(840, 650))
        dis_step.SetFont(font11)
        col3.Add(dis_step)
        col3hor = wx.BoxSizer(wx.HORIZONTAL)
        col3hor_1 = wx.BoxSizer(wx.VERTICAL)
        col3hor_2 = wx.BoxSizer(wx.VERTICAL)
        col3hor_3 = wx.BoxSizer(wx.VERTICAL)
        dis_step_txt = wx.StaticText(self.mainpanel, label="Distance step, dx:")
        dis_step_txt.SetFont(font11light)
        col3hor_1.Add(dis_step_txt, 0, wx.TOP, 5)
        timestep_txt = wx.StaticText(self.mainpanel, label='Time step, dt:')
        timestep_txt.SetFont(font11light)
        col3hor_1.Add(timestep_txt, 0, wx.TOP, 5)
        iteration_txt = wx.StaticText(self.mainpanel, label='Iteration:')
        iteration_txt.SetFont(font11light)
        col3hor_1.Add(iteration_txt, 0, wx.TOP, 5)
        # stability_txt = wx.StaticText(self.mainpanel, label='Stability test (./.<0.5)', pos=(65, 690))
        # stability_txt.SetFont(font11light)
        # col3hor_1.Add(stability_txt, 0, wx.TOP, 5)
        self.dis_step_input = wx.TextCtrl(self.mainpanel, pos=(230, 640), size=(70, 20))
        self.timestep_input = wx.TextCtrl(self.mainpanel, pos=(230, 665), size=(70, 20))
        self.iteration_input = wx.TextCtrl(self.mainpanel, pos=(230, 665), size=(70, 20))
        # self.stability_input = wx.TextCtrl(self.mainpanel, pos=(230, 690), size=(70, 20), style=wx.TE_READONLY)
        self.dis_step_input.SetFont(font11light)
        self.timestep_input.SetFont(font11light)
        self.iteration_input.SetFont(font11light)
        # self.stability_input.SetFont(font11light)
        col3hor_2.Add(self.dis_step_input, 0, wx.TOP, 0)
        col3hor_2.Add(self.timestep_input, 0, wx.TOP, 5)
        col3hor_2.Add(self.iteration_input, 0, wx.TOP, 5)
        # col3hor_2.Add(self.stability_input, 0, wx.TOP, 5)
        dis_step_unit = wx.StaticText(self.mainpanel, label='µm')
        timestep_unit = wx.StaticText(self.mainpanel, label='hour')
        dis_step_unit.SetFont(font11light)
        timestep_unit.SetFont(font11light)
        col3hor_3.Add(dis_step_unit, 0, wx.TOP, 5)
        col3hor_3.Add(timestep_unit, 0, wx.TOP, 5)
        run_button = wx.Button(self.mainpanel, label="Run!", size=(125, 75))
        font18 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        run_button.SetFont(font18)
        run_button.SetBackgroundColour('sea green')
        run_button.SetForegroundColour('white')
        run_button.Bind(wx.EVT_BUTTON, self.OnRun)
        col3hor.Add(col3hor_1)
        col3hor.Add(col3hor_2, 0, wx.LEFT, 10)
        col3hor.Add(col3hor_3, 0, wx.LEFT, 10)
        col3.Add(col3hor, 0, wx.TOP, 5)
        col3.Add(run_button, 0, wx.TOP, 5)
        colData.Add(col3, 0, wx.LEFT, 100)

        input_sizer.Add(colData, 0, wx.TOP, 20)

        # ============================= OUTPUT BOX =====================================
        # Text: Output
        Output = wx.StaticText(self.mainpanel, label='Model fits:', pos=(30, 800))
        font14 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        Output.SetFont(font14)
        Output.SetForegroundColour('red')
        model_sizer.Add(Output, 0, wx.LEFT, 20)
        # ----------------------- PLOT MODEL -----------------------------------------
        self.figure_pic2 = wx.StaticBitmap(self.mainpanel, pos=(30, 295))
        self.figure_pic2.SetBitmap(wx.Bitmap('images/Blank.png'))
        self.outPutPlot = wx.BoxSizer(wx.HORIZONTAL)
        self.outPutPlot.Add(self.figure_pic2)
        model_sizer.Add(self.outPutPlot, 0, wx.ALL, 20)
        # ----------------------- Results --------------------------------------------
        model_hor = wx.BoxSizer(wx.HORIZONTAL)
        model_hor_1 = wx.BoxSizer(wx.VERTICAL)
        model_hor_2 = wx.BoxSizer(wx.VERTICAL)
        model_hor_3 = wx.BoxSizer(wx.VERTICAL)
        model_hor_4 = wx.BoxSizer(wx.HORIZONTAL)
        bestfittime_txt = wx.StaticText(self.mainpanel, label="Best fit time:")
        uncertainty_txt = wx.StaticText(self.mainpanel, label="Uncertainty:")
        bestfittime_txt.SetFont(font11)
        uncertainty_txt.SetFont(font11)
        plus_txt = wx.StaticText(self.mainpanel, label="plus")
        minus_txt = wx.StaticText(self.mainpanel, label="minus")
        plus_txt.SetFont(font11)
        minus_txt.SetFont(font11)
        model_hor_1.Add(bestfittime_txt, 0, wx.TOP, 0)
        model_hor_1.Add(uncertainty_txt, 0, wx.TOP, 5)
        model_hor_1.Add(plus_txt, 0, wx.TOP | wx.ALIGN_RIGHT, 5)
        model_hor_1.Add(minus_txt, 0, wx.TOP | wx.ALIGN_RIGHT, 5)
        self.bestfittime_output = wx.TextCtrl(self.mainpanel, style=wx.TE_READONLY, size=(70, 20))
        self.plus_output = wx.TextCtrl(self.mainpanel, style=wx.TE_READONLY, size=(70, 20))
        self.minus_output = wx.TextCtrl(self.mainpanel, style=wx.TE_READONLY, size=(70, 20))
        self.bestfittime_output.SetFont(font11light)
        self.plus_output.SetFont(font11light)
        self.minus_output.SetFont(font11light)
        model_hor_2.Add(self.bestfittime_output)
        model_hor_2.Add(self.plus_output, 0, wx.TOP, 25)
        model_hor_2.Add(self.minus_output, 0, wx.TOP, 5)
        hours_unit1 = wx.StaticText(self.mainpanel, label="hours")
        hours_unit2 = wx.StaticText(self.mainpanel, label="hours")
        hours_unit3 = wx.StaticText(self.mainpanel, label="hours")
        hours_unit1.SetFont(font11light)
        hours_unit2.SetFont(font11light)
        hours_unit3.SetFont(font11light)
        model_hor_3.Add(hours_unit1)
        model_hor_3.Add(hours_unit2, 0, wx.TOP, 30)
        model_hor_3.Add(hours_unit3, 0, wx.TOP, 5)
        day_text1 = wx.StaticText(self.mainpanel, label="(~")
        self.day_output = wx.TextCtrl(self.mainpanel, style=wx.TE_READONLY, size=(70, 20))
        day_text2 = wx.StaticText(self.mainpanel, label="days)")
        day_text1.SetFont(font11light)
        self.day_output.SetFont(font11light)
        day_text2.SetFont(font11light)
        model_hor_4.Add(day_text1)
        model_hor_4.Add(self.day_output, 0, wx.LEFT, 10)
        model_hor_4.Add(day_text2, 0, wx.LEFT, 10)

        model_hor.Add(model_hor_1)
        model_hor.Add(model_hor_2, 0, wx.LEFT, 20)
        model_hor.Add(model_hor_3, 0, wx.LEFT, 10)
        model_hor.Add(model_hor_4, 0, wx.LEFT, 20)
        model_sizer.Add(model_hor, 0, wx.LEFT | wx.TOP, 20)

        mainsizer.Add(heading_sizer_main)
        mainsizer.Add(wx.StaticLine(self.mainpanel,), 0, wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(instruction_sizer, 0, wx.ALL, 5)
        mainsizer.Add(wx.StaticLine(self.mainpanel, ), 0, wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(input_sizer, wx.CENTER)
        mainsizer.Add(wx.StaticLine(self.mainpanel, ), 0, wx.ALL | wx.EXPAND, 20)
        mainsizer.Add(model_sizer)

        programsizer.Add(mainsizer, 0, wx.CENTER, 0)

        self.mainpanel.SetSizer(programsizer)
        self.fig = make_subplots(rows=1, cols=3)
        self.length = 0
        self.meas_profile = np.zeros((3, self.length))
        self.meas_dis = 0
        self.err = 0
        self.tilt_value = 0     # in degree
        self.DCl = 0
        self.DF = 0
        self.DOH = 0
        self.num_upload = 0     # number of times pressing Upload and Plot Data button
        self.num_plot = 0       # number of times pressing Plot button
        self.num_run = 0        # number of times pressing Run! button

    def OnDataTemplate(self, event):
        path = 'Data Template.csv'
        os.startfile(path)

    def OnUpload(self, event):
        path = 'Upload.csv'
        os.startfile(path)

    def OnPlotData(self, event):
        with open("Upload.csv", 'r') as fid:
            self.meas_dis = []
            lines = fid.readlines()
            self.length = len(lines)-1
            self.meas_profile = np.zeros((3, self.length))    # array 3x19
            self.err = np.zeros((3, self.length))             # array 3x19
            i = 0
            for line in lines[1:]:
                self.meas_dis.append(i)
                line = line.strip().split(',')
                self.meas_profile[:, i] = np.array(line[1:4])
                self.err[:, i] = np.array(line[4:])
                i += 1

        # update num_upload, num_plot, num_run
        self.num_upload += 1
        if self.num_upload > 1:    # if true, reset all value
            self.num_upload = 1
            self.num_plot = 0
            self.num_run = 0

        self.fig = make_subplots(rows=1, cols=3)

        # PLOT fig 1. Cl
        for kk in range(1):
            self.fig.add_trace(go.Scatter(x=self.meas_dis,
                                          y=self.meas_profile[kk, :],
                                          error_y=dict(array=self.err[kk], visible=True, color="black"),
                                          mode="lines+markers",
                                          name="Natural data Cl",
                                          line=dict(color="black", dash="dash", width=2),
                                          ),
                               row=1, col=1)

            self.fig.update_yaxes(title_text="X(Cl)", row=1, col=1, titlefont=dict(size=12), tickfont=dict(size=12))
            self.fig.update_xaxes(title_text="Distance (µm)", row=1, col=1, titlefont=dict(size=12), tickfont=dict(size=12))

        # PLOT fig. 2 F
        for kk in range(1, 2):
            self.fig.add_trace(go.Scatter(x=self.meas_dis,
                                          y=self.meas_profile[kk, :],
                                          error_y=dict(array=self.err[kk], visible=True, color="black"),
                                          mode="lines+markers",
                                          name="Natural data Cl",
                                          line=dict(color="black", dash="dash", width=2),
                                          ),
                               row=1, col=2)

            self.fig.update_yaxes(title_text="X(F)", row=1, col=2, titlefont=dict(size=12), tickfont=dict(size=12))
            self.fig.update_xaxes(title_text="Distance (µm)", row=1, col=2, titlefont=dict(size=12), tickfont=dict(size=12))

        # PLOT fig. 3 OH
        for kk in range(2, 3):
            self.fig.add_trace(go.Scatter(x=self.meas_dis,
                                          y=self.meas_profile[kk, :],
                                          error_y=dict(array=self.err[kk], visible=True, color="black"),
                                          mode="lines+markers",
                                          name="Natural data Cl",
                                          line=dict(color="black", dash="dash", width=2),
                                          ),
                               row=1, col=3)

            self.fig.update_yaxes(title_text="X(OH)", row=1, col=3, titlefont=dict(size=12), tickfont=dict(size=12))
            self.fig.update_xaxes(title_text="Distance (µm)", row=1, col=3, titlefont=dict(size=12), tickfont=dict(size=12))

            self.fig['layout'].update(width=1230, height=400, autosize=False)
            self.fig.update_layout(showlegend=False)
            self.fig.update_yaxes(dtick=0.01, row=1, col=1)
            self.fig.update_yaxes(dtick=0.05, row=1, col=2)
            self.fig.update_yaxes(dtick=0.05, row=1, col=3)
            self.fig.update_xaxes(dtick=2)
            self.fig.write_image("images/plot.png")

            self.figure_pic1.SetBitmap(wx.Bitmap('images/plot.png'))

    def OnCalculateDiff(self, event):
        self.tilt_value = math.radians(float(self.tilt_input.GetValue()))
        self.DCl = 5.1*10**(-5)*math.exp(-290000/(8.314*(float(self.temp_input.GetValue())+273.15)))*\
                  math.pow(math.cos(self.tilt_value), 2)
        DCl = str(self.DCl).split('e')

        self.DF = 9*10**(-5)*math.exp(-288000/(8.314*(float(self.temp_input.GetValue())+273.15)))*\
                  math.pow(math.cos(self.tilt_value), 2)
        DF = str(self.DF).split('e')

        self.DOH = 1.7*10**(-2)*math.exp(-397000/(8.314*(float(self.temp_input.GetValue()) + 273.15)))*\
                  math.pow(math.cos(self.tilt_value), 2)
        DOH = str(self.DOH).split('e')

        DCl = 'e'.join([str(round(float(DCl[0]), 2)), DCl[1]])
        DF = 'e'.join([str(round(float(DF[0]), 2)), DF[1]])
        DOH = 'e'.join([str(round(float(DOH[0]), 2)), DOH[1]])
        self.DCl_input.SetValue(DCl)
        self.DF_input.SetValue(DF)
        self.DOH_input.SetValue(DOH)

    def OnPlot(self, event):
        try:
            XCl_ini = float(self.XCl_ini_input.GetValue())
            XF_ini = float(self.XF_ini_input.GetValue())
            XOH_ini = float(self.XOH_ini_input.GetValue())
            XCl_left = float(self.XCl_left_input.GetValue())
            XF_left = float(self.XF_left_input.GetValue())
            XOH_left = float(self.XOH_left_input.GetValue())
            XCl_right = float(self.XCl_right_input.GetValue())
            XF_right = float(self.XF_right_input.GetValue())
            XOH_right = float(self.XOH_right_input.GetValue())

            self.num_plot += 1

            with open('previousIniBound.txt', 'w') as prevFile:
                prevFile.write(str(XCl_ini)+','+str(XCl_left)+','+str(XCl_right)+'\n')
                prevFile.write(str(XF_ini)+','+str(XF_left)+','+str(XF_right)+'\n')
                prevFile.write(str(XOH_ini)+','+str(XOH_left)+','+str(XOH_right)+'\n')
        except ValueError:
            self.valueErrorInibound()

        if self.num_plot > 1:
            # Try to update traces
            self.fig.update_traces(go.Scatter(x=[0, 0, self.length, self.length],
                                              y=[XCl_left, XCl_ini, XCl_ini, XCl_right]),
                                   selector=dict(name='Blue 1'))
            self.fig.update_traces(go.Scatter(x=[0, 0, self.length, self.length],
                                              y=[XF_left, XF_ini, XF_ini, XF_right]),
                                   selector=dict(name='Blue 2'))
            self.fig.update_traces(go.Scatter(x=[0, 0, self.length, self.length],
                                              y=[XOH_left, XOH_ini, XOH_ini, XOH_right]),
                                   selector=dict(name='Blue 3'))
            self.fig.write_image("images/plot.png")
            self.figure_pic1.SetBitmap(wx.Bitmap('images/plot.png'))
        else:
            # If cannot, add traces
            self.fig.add_trace(go.Scatter(x=[0, 0, self.length, self.length],
                                          y=[XCl_left, XCl_ini, XCl_ini, XCl_right],
                                          name='Blue 1',
                                          line_shape='linear',
                                          line=(dict(color='blue', dash='dash', width=1))),
                               row=1, col=1)
            self.fig.add_trace(go.Scatter(x=[0, 0, self.length, self.length],
                                          y=[XF_left, XF_ini, XF_ini, XF_right],
                                          name='Blue 2',
                                          line_shape='linear',
                                          line=(dict(color='blue', dash='dash', width=1))),
                               row=1, col=2)
            self.fig.add_trace(go.Scatter(x=[0, 0, self.length, self.length],
                                          y=[XOH_left, XOH_ini, XOH_ini, XOH_right],
                                          name='Blue 3',
                                          line_shape='linear',
                                          line=(dict(color='blue', dash='dash', width=1))),
                               row=1, col=3)
            self.fig.write_image("images/plot.png")
            self.figure_pic1.SetBitmap(wx.Bitmap('images/plot.png'))

    def OnRun(self, event):
        dx = float(self.dis_step_input.GetValue())
        dt = float(self.timestep_input.GetValue())

        t_length = int(int(self.iteration_input.GetValue())*dt)

        self.num_run += 1

        # --------Reading INITIAL initial_boundary data----------
        conc_i = np.zeros((3, 2))     # array 3x2
        conc_i[0][0] = float(self.XCl_left_input.GetValue())
        conc_i[0][1] = float(self.XCl_right_input.GetValue())
        conc_i[1][0] = float(self.XF_left_input.GetValue())
        conc_i[1][1] = float(self.XF_right_input.GetValue())
        conc_i[2][0] = float(self.XOH_left_input.GetValue())
        conc_i[2][1] = float(self.XOH_right_input.GetValue())
        a = [0, self.length]
        component = 3
        gamma = 0
        num_to1 = 1e-12
        dt0 = 1
        # --- Reading Boundary & Interface conditions for each component ---
        with open('Boundary.txt', 'r') as fid:
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

        # ------ Reading time-Temperature-Interface velocity data -----

        # -------------- Reading DIFFUSION COEFFICIENT data---------------
        D0_L = [self.DCl, self.DF, self.DOH]
        D0_R = [self.DCl, self.DF, self.DOH]
        # converting unit of D
        hr2sec = 60 * 60
        # converting D into um^2/hours
        D0_L = list(map(lambda x: x * (1e+12 * hr2sec), D0_L))
        D0_R = list(map(lambda x: x * (1e+12 * hr2sec), D0_R))
        temp_input = float(self.temp_input.GetValue())
        temp = [temp_input, temp_input]
        # converting 'Celsius' to 'Kelvin'
        temp = list(map(lambda t: t + 273.15, temp))
        time = [0, t_length]      # in years---how to get this data

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
        Intf_pos = 0
        Intf_ind = xip.index(Intf_pos)
        # checking the position of Interfaces: xip[0] < Intf_ind < xip[end]
        if Intf_ind < 1:
            Intf_ind = 1
        if Intf_ind > len(xip) - 1:
            Intf_ind = len(xip) - 2
        Intf_ind0 = Intf_ind  # to store the initial interface pos.

        # position of cell-centers
        xcp = np.zeros((len(xip) - 1))
        for k in range(len(xip) - 1):
            xcp[k] = xip[k] + dx / 2

            # stroing in app. variables
            x = np.array(xcp)
            xnum = len(x)
            xsize = xip[-1] - xip[0]
            # total time-period for computtion

            # Setting initial concentration profile(s)
            # pre-allocating the vectors
            C_i = np.zeros((component, xnum))
            # setting initial profile

            # Flat homogeneous initial concentration in each medium
            for j in range(component):
                for i in range(xnum):
                    if i < Intf_ind:
                        C_i[j, i] = conc_i[j, 0]
                    elif i >= Intf_ind:
                        C_i[j, i] = conc_i[j, -1]

            # Total initial concentration for mass-balance check
            x_mb = np.array(x).reshape(len(x), 1)
            mass0 = np.zeros((component, 1))
            for kk in range(component):
                if kk == 0:
                    for i in range(xnum):
                        mass0[kk] += C_i[kk, i] * x_mb[i] ** gamma * dx
                if kk == 1:
                    for i in range(xnum):
                        mass0[kk] += C_i[kk, i] * x_mb[i] ** gamma * dx
                if kk == 2:
                    for i in range(xnum):
                        mass0[kk] += C_i[kk, i] * x_mb[i] ** gamma * dx

            # Plotting initial profile and printing certain details
            C_plot = C_i.transpose()

        # PLOT AND RUN THE MODEL
        pq = Intf_ind  # for shortening the variable name
        # Plot Fig. 1 Cl
        for kk in range(1):
            if self.num_run == 1:
                if pq > 0:
                    self.fig.add_trace(
                        go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                                   y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                      list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
                                   mode="lines",
                                   name='Model 1',
                                   line=dict(color='red')),
                        row=1, col=1)

                else:
                    self.fig.add_trace(go.Scatter(x=xcp,
                                                  y=C_plot[:, kk],
                                                  mode="lines",
                                                  name='Model 1',
                                                  line=dict(color='red')),
                                       row=1, col=1)
            else:
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                      list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]),
                                           selector=dict(name='Model 1'))
                else:
                    self.fig.update_traces(go.Scatter(
                        x=xcp,
                        y=C_plot[:, kk]),
                        selector=dict(name='Model 1'))

            DCl = str(self.DCl).split('e')
            DCl = 'e'.join([str(round(float(DCl[0]), 2)), DCl[1]])
            D_Cl_str = 'D(Cl) =' + str(DCl) + ' m²/s'
            x_ano_1 = 3 * self.length / 4
            y_ano_1 = 31 * self.meas_profile[kk][kk] / 32

            self.fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                          y=[y_ano_1, ],
                                          mode="markers+text",
                                          text=[D_Cl_str, ],
                                          textfont=dict(size=9),
                                          line=dict(color="white"),
                                          showlegend=False),
                               row=1, col=1)

        # PLOT fig. 2 F
        for kk in range(1, 2):
            if self.num_run == 1:
                if pq > 0:
                    self.fig.add_trace(
                        go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                                   y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                      list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
                                   mode="lines",
                                   name='Model 2',
                                   line=dict(color='red')),
                        row=1, col=2)
                else:
                    self.fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                                  y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]],
                                                  mode="lines",
                                                  name='Model 2',
                                                  line=dict(color='red')),
                                       row=1, col=2)
            else:
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                      list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]),
                        selector=dict(name='Model 2'))
                else:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], xcp, xip[-1]],
                        y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]),
                        selector=dict(name='Model 2'))

            DF = str(self.DF).split('e')
            DF = 'e'.join([str(round(float(DF[0]), 2)), DF[1]])
            D_F_str = 'D(F) =' + str(DF) + ' m²/s'
            x_ano_1 = 3 * self.length / 4
            y_ano_1 = 31 * self.meas_profile[kk][kk] / 32

            self.fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                          y=[y_ano_1, ],
                                          mode="markers+text",
                                          text=[D_F_str, ],
                                          textfont=dict(size=9),
                                          line=dict(color="white"),
                                          showlegend=False),
                               row=1, col=2)
        # PLOT fig. 3 OH
        for kk in range(2, 3):
            if self.num_run == 1:
                if pq > 0:
                    self.fig.add_trace(
                        go.Scatter(x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                                   y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                                      list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]],
                                   mode="lines",
                                   name='Model 3',
                                   line=dict(color='red')),
                        row=1, col=3)
                else:
                    self.fig.add_trace(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                                  y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]],
                                                  mode="lines",
                                                  name='Model 3',
                                                  line=dict(color='red')),
                                       row=1, col=3)
            else:
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                          list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]),
                        selector=dict(name='Model 3'))
                else:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], xcp, xip[-1]],
                        y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]),
                        selector=dict(name='Model 3'))

            DOH = str(self.DOH).split('e')
            DOH = 'e'.join([str(round(float(DOH[0]), 2)), DOH[1]])
            D_OH_str = 'D(OH) =' + str(DOH) + ' m²/s'
            x_ano_1 = 3 * self.length / 4
            y_ano_1 = 31 * self.meas_profile[kk][kk] / 32

            self.fig.add_trace(go.Scatter(x=[x_ano_1, ],
                                          y=[y_ano_1, ],
                                          mode="markers+text",
                                          text=[D_OH_str, ],
                                          textfont=dict(size=9),
                                          line=dict(color="white"),
                                          showlegend=False),
                               row=1, col=3)

        # =================== MAIN CALCULATION =========================
        # variables storing evolution of parameters
        C_f = np.zeros((component, xnum))  # final concentration matrix
        time_evo = []
        T_evo = []
        time_evo.append(0)  # time evolution record
        T_evo.append(temp[0])  # Temp evolution record

        # converting 'phi=' from row to column vector so as to match
        # with dimensions of 'phin' for ease of programming
        # size (phi0/phin) = matrix (xnum, component)
        phi0 = C_i.transpose()
        phin = np.zeros((len(phi0), len(phi0[0])))
        timesum = 0  # total real time elapsed
        t = 0  # iteration/time-step index
        Ans_Cl = np.zeros((len(phi0), t_length))
        Ans_F = np.zeros((len(phi0), t_length))
        Ans_OH = np.zeros((len(phi0), t_length))

        # Main Computation starts
        while timesum < t_length:
            t = t + 1  # increasing the iteration index
            if t % 50 == 0:
                print('     ... {} iteration ... \n'.format(t))
            # Calculating Temperature
            for i in range(1, len(time)):
                if (time[i - 1] - num_to1) <= timesum <= (time[i] + num_to1):
                    Tslope = (temp[i] - temp[i - 1]) / (time[i] - time[i - 1])
                    Tintercept = temp[i - 1] - (Tslope * time[i - 1])
                    T_rock = Tslope * timesum + Tintercept

            # Calculating the TIME-STEP (dt)
            dt = min(dt0, t_length - timesum)  # given time-step is dt0

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
            for gg in range(component - 1):

                # MC_D-coeff terms for appro. component from D_matrix
                # calculating terms from D_matrix for a component

                # D11     D12     D13     D14  .... D1(n-1)
                # D21     D22     D23     D24  .... D2(n-1)
                # ...
                # D(n-1)1 D(n-1)2 D(n-1)3 D(n-1)4 . D(n-1)(n-1)
                # e.g for component 1; D11, D12, D13, ..., D1(n-1) will be calculated at
                # new time step, i.e. implicit time
                # component index should be used to identify the component

                MC_D = np.zeros((component - 1, xnum))
                for i in range(0, xnum):
                    sig_DX = 0
                    for k in range(0, component):
                        sig_DX = sig_DX + D_xcp[k, i] * phi0[i, k]
                    for hh in range(0, component - 1):
                        # Kronecker delta
                        Kro_del = 0
                        if gg == hh:
                            Kro_del = 1
                        term1 = D_xcp[gg, i] * Kro_del
                        term2 = ((D_xcp[gg, i] * phi0[i, gg]) / sig_DX) * (D_xcp[hh, i] - D_xcp[component - 1, i])
                        # by default last component will be taken as dependent component
                        MC_D[hh, i] = term1 - term2

                # interpolating D at cell-interfaces from surrounding cell-centres
                D_xip_0 = np.zeros((component - 1, len(xip)))
                for m in range(0, component - 1):
                    for j in range(1, len(xip) - 1):
                        D_xip_0[m, j] = (2 * MC_D[m, j - 1] * MC_D[m, j]) / (MC_D[m, j - 1] + MC_D[m, j])
                        # putting the immediate next D values for domain boundaries
                        D_xip_0[m, 0] = D_xip_0[m, 1]
                        D_xip_0[m, -1] = D_xip_0[m, xnum - 1]

                # storing D_xip_0 into the working variable
                D_xip = D_xip_0

                # Assigning boundary, flux & interface cond. for each component
                BC_left = Bound_left[gg]
                flux_left = F_left[gg]
                BC_right = Bound_right[gg]
                flux_right = F_right[gg]

                # Numerical solution
                L = np.zeros((xnum, xnum))  # matrix of the coefficients
                R = np.zeros((xnum, 1))  # right hand side vector
                # Space Loop starts
                for i in range(0, xnum):
                    # Defining the boundaries by FVM EQUATIONS
                    if i == 0:  # LEFT BOUNDARY CONDITION
                        if BC_left == 1:  # fixed concentration
                            A3 = 0
                            rRri = 0
                            off_D_term = 0
                        elif BC_left == 2:  # zero flux
                            # diagonal D_terms for L Matrix
                            Dr = D_xip[gg, i + 1]
                            A3 = Dr * dt / dx ** 2
                            rRri = ((x[i] + 0.5 * dx) / x[i]) ** gamma

                            # off diagonal D_terms for RHS coefficients
                            off_D_term = 0
                            for hh in range(0, component - 1):
                                if hh == gg:
                                    off_D_term = 0
                                else:
                                    B3 = D_xip[hh, i + 1] * dt / dx ** 2
                                    # adding all off-diagonal terms
                                    off_D_term = off_D_term + (
                                                (B3 * rRri * phi0[i + 1, hh]) - (B3 * rRri * phi0[i, hh]))
                        # MATRIX
                        L[i, i] = 1 + (A3 * rRri)
                        L[i, i + 1] = -A3 * rRri
                        # RHS coefficients
                        R[i, 0] = phi0[i, gg] + off_D_term

                    elif i == xnum - 1:  # RIGHT BOUNDARY CONDITION
                        if BC_right == 1:  # fixed concentration
                            A1 = 0
                            rLri = 0
                            off_D_term = 0
                        elif BC_right == 2:  # zero flux
                            # diagonal D_terms for L Matrix
                            Dl = D_xip[gg, i]
                            A1 = Dl * dt / dx ** 2
                            rLri = ((x[i] - 0.5 * dx) / x[i]) * gamma

                            # off diagonal D_terms for RHS coefficients
                            off_D_term = 0
                            for hh in range(0, component - 1):
                                if hh == gg:
                                    off_D_term = 0
                                else:
                                    B1 = D_xip[hh, i] * dt / dx ** 2
                                    # adding all off-diagonal terms
                                    off_D_term = off_D_term * (
                                                (B1 * rLri * phi0[i - 1, hh]) - (B1 * rLri * phi0[i, hh]))

                        # MATRIX
                        L[i, i - 1] = -A1 * rLri
                        L[i, i] = 1 + (A1 * rLri)
                        # RHS coefficients
                        R[i, 0] = phi0[i, gg] + off_D_term

                    else:  # INTERNAL NODES
                        # diagonal D_terms
                        Dl = D_xip[gg, i]
                        Dr = D_xip[gg, i + 1]
                        A1 = Dl * dt / dx ** 2
                        A3 = Dr * dt / dx ** 2
                        # radius_terms
                        rLri = ((x[i] - 0.5 * dx) / x[i]) ** gamma
                        rRri = ((x[i] + 0.5 * dx) / x[i]) ** gamma

                        # MATRIX coefficients
                        L[i, i - 1] = -A1 * rLri
                        L[i, i] = 1 + (A1 * rLri) + (A3 * rRri)
                        L[i, i + 1] = -A3 * rRri

                        # RHS VECTOR
                        # off diagonal D_terms
                        off_D_term = 0
                        for hh in range(0, component - 1):
                            if hh == gg:
                                off_D_term = 0
                            else:
                                B1 = D_xip[hh, i] * dt / dx ** 2
                                B3 = D_xip[hh, i + 1] * dt / dx ** 2
                                # adding all off-diagonal terms
                                off_D_term = off_D_term * \
                                             ((B1 * rLri * phi0[i - 1, hh]) -
                                              ((B1 * rLri + B3 * rRri) * phi0[i, hh]) +
                                              (B3 * rRri * phi0[i + 1, hh]))
                        R[i, 0] = phi0[i, gg] + off_D_term

                # SPACE LOOP ENDS

                # computing the matrix
                phin[:, gg] = list(np.matmul(np.linalg.inv(L), R))

                # calculating the concentration of the dependent component
            for i in range(xnum):
                sum_IndComp = 0
                for hh in range(component - 1):
                    sum_IndComp = sum_IndComp + phin[i, hh]
                phin[i, -1] = 1.0 - sum_IndComp
                # saving to initial profile
            phi0 = phin

            # plotting
            C_plot = phin
            Ans_Cl[:, timesum] = phin[:, 0]
            Ans_F[:, timesum] = phin[:, 1]
            Ans_OH[:, timesum] = phin[:, 2]

            # ------------------- START PLOTTING ------------------------
            # PLOT fig 1. Cl
            for kk in range(1):
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                          list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]),
                        selector=dict(name='Model 1'))

                else:
                    self.fig.update_traces(go.Scatter(x=xcp, y=C_plot[:, kk]), selector=dict(name='Model 1'))

            # PLOT fig. 2 F
            for kk in range(1, 2):
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk], ] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                          list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]), selector=dict(name='Model 2'))

                else:
                    self.fig.update_traces(
                        go.Scatter(x=[xip[0], xcp, xip[-1]], y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]),
                        selector=dict(name='Model 2'))

            # PLOT fig. 3 OH
            for kk in range(2, 3):
                if pq > 0:
                    self.fig.update_traces(go.Scatter(
                        x=[xip[0], ] + list(xcp[0:pq]) + [xip[pq], xip[pq], ] + list(xcp[pq:xnum]) + [xip[-1]],
                        y=[C_plot[0, kk]] + list(C_plot[0:pq, kk]) + [C_plot[pq - 1, kk], C_plot[pq, kk]] + \
                           list(C_plot[pq:xnum, kk]) + [C_plot[xnum - 1, kk]]), selector=dict(name='Model 3'))
                else:
                    self.fig.update_traces(go.Scatter(x=[xip[0], xcp, xip[-1]],
                                                      y=[C_plot[1, kk], C_plot[:, kk], C_plot[xnum, kk]]),
                                                      selector=dict(name='Model 3'))

                # FINISH PLOTTING...................

            # update iterator
            timesum = timesum + dt
            time_evo.append(timesum)
            T_evo.append(T_rock)

        # FIND THE BEST FIT W.R.T Cl
        num_errs = []
        min_rms = 100
        # location of model points
        x_model = []
        i = 0
        while i < self.length:
            x_model.append(i)
            i += dx

        for j in range(t_length):
            Ans = list(Ans_Cl[:, j])
            print("* ", j, "\t Ans: ", Ans)
            interp_funct = interp1d(x_model, Ans)
            new_Ans = list(interp_funct(self.meas_dis))
            print("* ", j, "\t new_Ans: ", new_Ans)
            num_fit = 0
            # FIND TE MAXIMUM POINTS OF 'FIT' WITHIN UNCERTAINTY
            for k in range(len(self.meas_dis)):
                if (new_Ans[k] < self.meas_profile[0][k] + self.err[0][k]) and \
                        (new_Ans[k] > self.meas_profile[0][k] - self.err[0][k]):
                    num_fit += 1
            print("* ", j, "\t num_fit: ", num_fit)
            num_errs.append(num_fit)

            # minimize root-mean-square deviation to find best fit timing
            rms = sum([(meas_profile - new_Ans) ** 2 for (meas_profile, new_Ans) in
                       list(zip(self.meas_profile[0], new_Ans))]) / self.length

            if rms < min_rms:
                min_rms = rms
                best_j = j

            print("* ", j, "\t best_j: ", best_j)
            print()

        if max(num_errs) == 0:
            self.rmsBox()

        print("BEST_J: ", max(num_errs))
        print("MAX NUM_FIT: {}. index: {}".format(max(num_errs), num_errs.index(max(num_errs))))

        # CALCULATE ERRORS IN THE RESULTS
        max_num_errs = max(num_errs)
        num_errs_reverse = num_errs[::-1]
        min_j = num_errs.index(max_num_errs)
        max_j = t_length - 1 - num_errs_reverse.index(max_num_errs)
        best_j = int((min_j + max_j)/2)

        print("min_j: ", min_j)
        print("max_j: ", max_j)
        print("best_j: ", best_j)
        negat_errs = min_j - best_j         # negative value
        posit_errs = max_j - best_j         # positive value
        t_best_hour = dt * best_j
        t_best_day = t_best_hour / 24
        t_best_ners = dt * negat_errs
        t_best_pers = dt * posit_errs
        t_best_day_ners = t_best_ners / 24
        t_best_day_pers = t_best_pers / 24
        best_Ans = Ans_Cl[:, best_j]
        min_Ans = Ans_Cl[:, min_j]
        max_Ans = Ans_Cl[:, max_j]
        print(best_j, "\t best_Ans: ", best_Ans)
        new_best_Ans = list(interp1d(x_model, best_Ans)(self.meas_dis))
        Diff = []
        Diff_norm = []
        for N in range(self.length):
            Diff.append(abs(new_best_Ans[N] - self.meas_profile[0][N]))
            Diff_norm.append(Diff[N] / self.meas_profile[0][N])
        Discrepancy = sum(Diff_norm)/len(Diff_norm)
        print("Discrepancy: ", Discrepancy)

        if self.num_run > 1:
            self.fig.update_traces(go.Scatter(x=xcp-dx/2, y=min_Ans), selector=dict(name='Min'))
            self.fig.update_traces(go.Scatter(x=xcp-dx/2, y=max_Ans), selector=dict(name='Max'))
        else:
            self.fig.add_trace(go.Scatter(x=xcp-dx/2,
                                          y=min_Ans,
                                          mode="lines",
                                          name='Min',
                                          line=dict(color='green', dash='dash', width=1)),
                               row=1, col=1)
            self.fig.add_trace(go.Scatter(x=xcp-dx/2,
                                          y=max_Ans,
                                          mode="lines",
                                          name='Max',
                                          line=dict(color='green', dash='dash', width=1)),
                               row=1, col=1)
        self.fig.update_traces(go.Scatter(x=xcp-dx/2, y=best_Ans), selector=dict(name='Model 1'))
        self.fig.update_traces(go.Scatter(x=xcp-dx/2, y=Ans_F[:, best_j]), selector=dict(name='Model 2'))
        self.fig.update_traces(go.Scatter(x=xcp-dx/2, y=Ans_OH[:, best_j]), selector=dict(name='Model 3'))

        self.fig.write_image("images/Model.png")
        self.figure_pic2.SetBitmap(wx.Bitmap('images/Model.png'))
        self.bestfittime_output.SetValue(str(round(t_best_hour, 5)))
        self.day_output.SetValue(str(round(t_best_day, 1)))
        self.plus_output.SetValue(str(round(t_best_pers, 5)))
        self.minus_output.SetValue(str(abs(round(t_best_ners, 5))))

    def rmsBox(self):
        wx.MessageBox("Check the number of iteration and initial/boundary conditions.", "Dialog", wx.OK|wx.ICON_ERROR)

    def valueErrorInibound(self):
        wx.MessageBox("Please key in all inputs for initial and boundary conditions.", "Dialog", wx.OK|wx.ICON_ERROR)

    def valueErrorTimestep(self):
        wx.MessageBox("Please enter an integer number for time step, dt.", "Dialog", wx.OK|wx.ICON_ERROR)


class App(wx.App):
    def OnInit(self):
        self.frame = Frame(parent=None, title="ApTimer")
        self.frame.Show()
        return True


app = App()
app.MainLoop()
import wx
import os


class Frame(wx.Frame):
    def __init__(self, parent, title):
        super(Frame, self).__init__(parent, title=title, size=(1300, 800))
        self.SetIcon(wx.Icon("images/icon.jpg", wx.BITMAP_TYPE_ANY))

        self.panel = Panel(self)


class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        self.SetBackgroundColour('white')

        self.InitUI()
        # =============================== HEADING ==========================================
        # Text: ApTimer
        font11 = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font11light = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        font10light = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        heading = wx.StaticText(self, label="ApTimer", pos=(170, 15))
        font18 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading.SetFont(font18)
        heading.SetForegroundColour('red')
        # Text: colon ':'
        colon = wx.StaticText(self, label=':', pos=(270, 15))
        colon.SetFont(font18)
        # Text: content of ApTimer
        content_txt = 'timescales of magmatic processes modelled from volatile diffusion in apatite'
        content = wx.StaticText(self, label=content_txt, pos=(290, 18))
        font16 = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        content.SetFont(font16)

        # ==================================== INSTRUCTION BOX ===================================
        # Text: Instruction
        instruction = wx.StaticText(self, label='Instruction:', pos=(50, 70))
        font12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        instruction.SetFont(font12)
        # Text: purpose
        purpose_txt1 = "This model aims to constrain the diffusion timescales related to magma ascent, using diffusion coefficients of F-Cl-OH in apatite determined from experiments at 800-1100°C,"
        purpose_txt2 = "1-atm by the authors below:"
        purpose1 = wx.StaticText(self, label=purpose_txt1, pos=(50, 100))
        purpose2 = wx.StaticText(self, label=purpose_txt2, pos=(50, 120))
        font12light = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        purpose1.SetFont(font12light)
        purpose2.SetFont(font12light)
        # Text: authors
        authors_txt = "Li W., Costa F., Chakraborty S., and Nagashima K. (2020) Multicomponent diffusion of F-Cl-OH in apatite and application to determining magma ascent rates. (DOI: ...)"
        authors = wx.StaticText(self, label=authors_txt, pos=(51, 155))
        authors.SetFont(font12light)

        # =========================== BOTTOM LINE =======================================
        bottom_txt = 'You are visitor number xx. If you encounter any problem using this webpage, please feel free to contact me (weiranli1991@gmail.com)'
        bottom = wx.StaticText(self, label=bottom_txt, pos=(50, 730))
        bottom.SetFont(font11light)

        # =============================== INPUT BOX =========================================
        # Text: Input
        Input = wx.StaticText(self, label='Input:', pos=(40,210))
        font14 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        Input.SetFont(font14)
        Input.SetForegroundColour('red')
        # -------------------- Text: Diffusion profiles: ------------------------------
        diff_profile = wx.StaticText(self, label='Diffusion profiles:', pos=(50, 240))
        diff_profile.SetFont(font11)
        please_use_txt = '*Please use the provided template (.csv) to organize your data, \nand upload them using the blue button below.'
        please_use = wx.StaticText(self, label=please_use_txt, pos=(50, 260))
        please_use.SetFont(font10light)
        # Data template button
        data_template = wx.Button(self, label='Data Template', pos=(50, 300), size=(120, 30))
        data_template.Bind(wx.EVT_BUTTON, self.OnDataTemplate)
        data_template.SetFont(font11)
        data_template.SetBackgroundColour('slate BLUE')
        data_template.SetForegroundColour('white')
        # Upload data button
        upload_data = wx.Button(self, label='Upload Data', pos=(200, 300), size=(120, 30))
        upload_data.Bind(wx.EVT_BUTTON, self.OnDataTemplate)
        upload_data.SetFont(font11)
        upload_data.SetBackgroundColour('sky blue')
        upload_data.SetForegroundColour('white')
        # Plot data button
        plot_data = wx.Button(self, label='Plot Data', pos=(350, 300), size=(120, 30))
        plot_data.Bind(wx.EVT_BUTTON, self.OnDataTemplate)
        plot_data.SetFont(font11)
        plot_data.SetBackgroundColour('steel blue')
        plot_data.SetForegroundColour('white')
        # ----------------------- Parameters used for modeling -----------------------
        parameter = wx.StaticText(self, label='Parameters used for diffusion modeling:', pos=(50, 350))
        parameter.SetFont(font11)
        # Temperature
        temperature = wx.StaticText(self, label='Temperature:', pos=(65, 375))
        temperature.SetFont(font11light)
        temp_input = wx.TextCtrl(self, pos=(280, 373), size=(70, 20))    # input field
        temp_input.SetFont(font11light)
        temp_unit = wx.StaticText(self, label='°C', pos=(360, 375))
        temp_unit.SetFont(font11light)
        # Tilt of traverse
        tilt = wx.StaticText(self, label='Tilt of traverse from the c-axis:', pos=(65, 400))
        tilt.SetFont(font11light)
        tilt_input = wx.TextCtrl(self, pos=(280, 398), size=(70, 20))
        tilt_input.SetFont(font11light)
        tilt_unit = wx.StaticText(self, label='degree', pos=(360, 400))
        tilt_unit.SetFont(font11light)
        # D(F) D(Cl) D(OH)
        DF = wx.StaticText(self, label='D(F)', pos=(230, 430))
        DF.SetFont(font11)
        DF_input = wx.TextCtrl(self, pos=(280, 428), size=(70, 20))
        DF_input.SetFont(font11light)   # ________________________
        DCl = wx.StaticText(self, label='D(Cl)', pos=(230, 455))
        DCl.SetFont(font11)
        DCl_input = wx.TextCtrl(self, pos=(280, 453), size=(70, 20))
        DCl_input.SetFont(font11light)  # ________________________
        DOH = wx.StaticText(self, label='D(OH)', pos=(230, 480))
        DOH.SetFont(font11)
        DOH_input = wx.TextCtrl(self, pos=(280, 478), size=(70, 20))
        DOH_input.SetFont(font11light)  # ________________________
        D_unit1 = wx.StaticText(self, label='m²/s', pos=(360, 430))
        D_unit2 = wx.StaticText(self, label='m²/s', pos=(360, 455))
        D_unit3 = wx.StaticText(self, label='m²/s', pos=(360, 480))
        D_unit1.SetFont(font11light)
        D_unit2.SetFont(font11light)
        D_unit3.SetFont(font11light)
        # Calculate diffusivity button
        calculate_diff = wx.Button(self, label='Calculate\ndiffusivity', pos=(65, 430), size=(150, 70))
        calculate_diff.SetFont(font11)
        calculate_diff.SetBackgroundColour('sea green')
        calculate_diff.SetForegroundColour('white')
        # -------------------- Initial conditions and Boundaries -----------------------
        XF_text = wx.StaticText(self, label="X(F)", pos=(65, 555))
        XF_text.SetFont(font11)
        XCl_text = wx.StaticText(self, label="X(Cl)", pos=(65, 580))
        XCl_text.SetFont(font11)
        XOH_text = wx.StaticText(self, label="X(OH)", pos=(65, 605))
        XOH_text.SetFont(font11)
        ini_text = wx.StaticText(self, label="Initial\nconditions:", pos=(120, 515))
        ini_text.SetFont(font11light)
        XF_ini_input = wx.TextCtrl(self, pos=(120, 555), size=(70, 20))
        XCl_ini_input = wx.TextCtrl(self, pos=(120, 580), size=(70, 20))
        XOH_ini_input = wx.TextCtrl(self, pos=(120, 605), size=(70, 20))
        left_text = wx.StaticText(self, label="Left\nboundary:", pos=(230, 515))
        left_text.SetFont(font11light)
        XF_left_input = wx.TextCtrl(self, pos=(230, 555), size=(70, 20))
        XCl_left_input = wx.TextCtrl(self, pos=(230, 580), size=(70, 20))
        XOH_left_input = wx.TextCtrl(self, pos=(230, 605), size=(70, 20))
        right_text = wx.StaticText(self, label="Right\nboundary:", pos=(340, 515))
        right_text.SetFont(font11light)
        XF_right_input = wx.TextCtrl(self, pos=(340, 555), size=(70, 20))
        XCl_right_input = wx.TextCtrl(self, pos=(340, 580), size=(70, 20))
        XOH_right_input = wx.TextCtrl(self, pos=(340, 605), size=(70, 20))
        # ----------------------- Last steps and run -----------------------------------
        dis_step_txt = wx.StaticText(self, label="Distance step, dx:", pos=(65, 640))
        dis_step_txt.SetFont(font11light)
        timestep_txt = wx.StaticText(self, label='Time step, dt:', pos=(65, 665))
        timestep_txt.SetFont(font11light)
        stability_txt = wx.StaticText(self, label='Stability test (./.<0.5)', pos=(65, 690))
        stability_txt.SetFont(font11light)
        dis_step_input = wx.TextCtrl(self, pos=(230, 640), size=(70, 20))
        timestep_input = wx.TextCtrl(self, pos=(230, 665), size=(70, 20))
        stability_input = wx.TextCtrl(self, pos=(230, 690), size=(70, 20))
        dis_step_unit = wx.StaticText(self, label='µm', pos=(310, 640))
        timestep_unit = wx.StaticText(self, label='second', pos=(310, 665))
        dis_step_unit.SetFont(font11light)
        timestep_unit.SetFont(font11light)
        run_button = wx.Button(self, label="Run!", pos=(380, 640), size=(90, 70))
        font18 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        run_button.SetFont(font18)
        run_button.SetBackgroundColour('sea green')
        run_button.SetForegroundColour('white')

        # ============================= OUTPUT BOX =====================================
        # Text: Output
        Output = wx.StaticText(self, label='Plotting data:', pos=(515, 210))
        font14 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        Output.SetFont(font14)
        Output.SetForegroundColour('red')
        # Plot image
        figure_pic = wx.StaticBitmap(self, pos=(520, 210))
        figure_pic.SetBitmap(wx.Bitmap('images/plot.png'))

    def OnDataTemplate(self, event):
        path = 'Data Template.csv'
        os.startfile(path)

    def InitUI(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        # INSTRUCTION BOX
        instruction_box = wx.PaintDC(self)
        instruction_box.SetPen(wx.Pen('black'))
        instruction_box.SetBrush(wx.Brush('white'))
        instruction_box.DrawRectangle(30, 60, 1220, 127)

        # INPUT BOX
        input_box = wx.PaintDC(self)
        input_box.SetPen(wx.Pen('black'))
        input_box.SetBrush(wx.Brush('white'))
        input_box.DrawRectangle(30, 200, 460, 520)

        # OUTPUT BOX
        output_box = wx.PaintDC(self)
        output_box.SetPen(wx.Pen('black'))
        output_box.SetBrush(wx.Brush('white'))
        output_box.DrawRectangle(505, 200, 745, 520)

        # Draw arrow
        arrow1 = wx.ClientDC(self)
        arrow1.DrawLine(175, 315, 195, 315)
        arrow2 = wx.ClientDC(self)
        arrow2.DrawLine(325, 315, 345, 315)
        # Draw line
        line1 = wx.ClientDC(self)
        line1.SetPen(wx.Pen('pale green'))
        line1.DrawLine(30, 340, 490, 340)
        line2 = wx.ClientDC(self)
        line2.SetPen(wx.Pen('pale green'))
        line2.DrawLine(30, 510, 490, 510)
        line3 = wx.ClientDC(self)
        line3.SetPen(wx.Pen('pale green'))
        line3.DrawLine(30, 633, 490, 633)


class App(wx.App):
    def OnInit(self):
        self.frame = Frame(parent=None, title="ApTimer")
        self.frame.Show()
        return True


app = App()
app.MainLoop()

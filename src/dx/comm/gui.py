# -*- coding: utf-8 -*-

import os
import wx

if os.name == 'nt':
    ICONE='dxcomm.ico'
else:
    ICONE='dxcomm.xpm'

class Taskbar(wx.App):
    """
    Classe: Taskbar
    Autor: João Alfredo Gama Batista <joaoalf@dotx.com.br>

    Gerencia o icone da barra de tarefas do systema (system tray)
    """
    ID_SOBRE=wx.NewId()
    ID_JANELA_SOBRE = wx.NewId()
    ID_CONFIG=wx.NewId()
    ID_EXIT=wx.NewId()

    def __init__(self, param):
        """Construtor da clase"""
        ##self.arq_icone = i
        self.param = param
        wx.App.__init__(self)

    def OnInit(self):
	"""Ativador da classe"""
        ##self._fsobre = wx.Frame(None, -1, "Sobre", size=(200, 150)) 
        self._taskbar = wx.TaskBarIcon()
        if os.name == 'nt':
            self._icone = wx.Icon(ICONE, wx.BITMAP_TYPE_ICO)
        else:
            self._icone = wx.Icon(ICONE, wx.BITMAP_TYPE_XPM)
            #self._icone.loadFromFile('dxcomm.ico')
        self._taskbar.SetIcon(self._icone, 'Integrador de sistemas dotX')
        wx.EVT_TASKBAR_RIGHT_UP(self._taskbar, self.OnTaskBarMenu)
        self._menu = wx.Menu()

        wx.EVT_MENU(self._taskbar, self.ID_SOBRE, self.OnSobre)
        wx.EVT_MENU(self._taskbar, self.ID_CONFIG, self.OnConfig)
        wx.EVT_MENU(self._taskbar, self.ID_EXIT, self.OnExit)

        self._menu.Append(self.ID_SOBRE, "Sobre...", "Sobre")
        self._menu.Append(self.ID_CONFIG, u"Configuração",
                                          u"Ajusta os parâmetros do sistema")
        self._menu.AppendSeparator()
        self._menu.Append(self.ID_EXIT, "Sair", "Sair")

        return True

    def OnTaskBarMenu(self, e):
        """Exibe o menu com opcoes do programa"""
        ##print "Clicou"
        self._taskbar.PopupMenu(self._menu)
        ##self._menu.Destroy()
        wx.GetApp().ProcessIdle()

    def OnExit(self, e=None):
        """Sair da aplicacao"""
        self._taskbar.RemoveIcon()
        self.ExitMainLoop()
        return True

    def OnSobre(self, e):
        """Mostra janela de creditos"""
        ws = Sobre(None, -1, 'Sobre...', 'dxCommd','2.1','Integrador de sistemas dotX', self.param)
        ws.Show(True)

    def OnConfig(self, e):
        """Exibe janela de configuracoes"""
        pass

class Sobre(wx.Frame):
    """
    Classe Sobre
    Autor: Joao Alfredo Gama Batista <joaoalf@dotx.com.br>

    Cria e gerencia a janela \"Sobre\".
    """
    titulo = u'Sobre...'
    LOGO = 'dxcommd_logo.png'

    def __init__(self, parent, id, title, nome, versao, descricao, param):
        """Construtor da classe"""
        self.param = param
        wx.Frame.__init__(self, parent, id, title, style=wx.CLOSE_BOX)
        panel_01 = wx.Panel(self, -1)
        panel_01.SetBackgroundColour(wx.Colour(255, 255, 255))
        #panel_02 = wx.Panel(self, -1)
        logo_img = wx.Image(os.path.join(self.param['principal.raiz'], self.LOGO), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self._logo = wx.StaticBitmap(panel_01, -1, logo_img, (0,0),(logo_img.GetWidth(),logo_img.GetHeight()))
        self._sobre_info1 = wx.StaticText(panel_01, -1, u"%s\nVersão: %s\n%s" % (nome, versao, descricao), style=wx.ALIGN_CENTRE)
        self._sobre_info2 = wx.StaticText(panel_01, -1, u"Todos os direitos reservados 2003, 2004 JJLR Consultoria e Serviços Ltda")
        self._botao_ok = wx.Button(panel_01, -1, 'OK')
        self.Bind(wx.EVT_BUTTON, self.OnExit, self._botao_ok)
        self._configurar()
        layout_01 = wx.BoxSizer(wx.VERTICAL)
        layout_02 = wx.BoxSizer(wx.HORIZONTAL)
        layout_03 = wx.BoxSizer(wx.HORIZONTAL)
        layout_01.Add(layout_02, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP)
        layout_01.Add(layout_03, 1, wx.ALIGN_BOTTOM|wx.EXPAND)
        layout_02.Add(self._logo, 0, wx.ALL, 10)
        layout_02.Add(self._sobre_info1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER|wx.ALL, 10)
        layout_03.Add(self._sobre_info2, 1, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT)
        layout_03.Add(self._botao_ok, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        
        #layout.Fit(panel)
        #self.SetAutoLayout(True)
        #panel.SetAutoLayout(True)
        
        #panel_02.SetAutoLayout(True)
        #panel_01.SetSizer(layout_02)
        #layout_02.Fit(panel_01)
        #panel_02.SetSizer(layout_03)
        #layout_03.Fit(panel_02)
        panel_01.SetSizer(layout_01)
        layout_01.SetSizeHints(panel_01)
        
        
        
        #layout_03.Fit(self)
        #
        #layout_02.SetSizeHints(panel_01)
        self.Fit()
        #panel_01.Fit()
        #panel_02.Fit()
        
        self.Layout()
        self.Centre()
                
    def _configurar(self):
        self._sobre_info1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self._sobre_info2.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        
         
    def OnExit(self, e=None):
        """Sair da aplicacao"""
        self.Destroy()
        #return True
        #self.Show(True)
        
    
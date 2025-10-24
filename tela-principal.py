import customtkinter as ctk # bibliotecas

janela = ctk.CTk() #cria uma nova janela


#Configuraçõe da janela
janela.title("Projeto de TCC - Analise de Controladores")
janela.geometry("700x400")

#Largura e altura máxima da tela do meu projeto
janela.maxsize(width=900, height=550) # definir largura máxima que posso abrir a tela
janela.minsize(width=500, height=250)
janela.resizable(width=True, height=True)


#customização da tela 

janela._set_appearance_mode('dark') #estilo da página


def nova_tela():
    nova_janela = ctk.CTkToplevel(janela, fg_color="teal")
    nova_janela.geometry(width =200, height = 200)

#frame
frame1 = ctk.CTkFrame(master=janela, width=200, height=200, fg_color="blue").place(x=10, y=20)

tabview = ctk.tabview = ctk.CTkTabview(janela, width=400, corner_radius=20, border_width=5)
tabview.place(x=10, y=10)

tabview.add('tab 1')  # add tab at the end
tabview.add('tab 2')  # add tab at the end
tabview.set('tab 2')  # set currently visible tab

button = ctk.CTkButton(master=tabview.tab('tab 1'))

button.place(x=10, y=10)
btn_novatela =  ctk.CTkButton(master=janela, text='Criterio',command=nova_tela).place(x=300, y=100)   

btn = ctk.CTkButton(janela, text='Olá')
btn.pack()


janela.mainloop()
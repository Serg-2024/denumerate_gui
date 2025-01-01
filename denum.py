import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
import pandas as pd

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("dark")
df_pow = pd.read_csv('powers.csv', sep=';', index_col='power')
df_nums = pd.read_csv('nums.csv', sep=';', index_col='num')

class Denum(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('800x450+300+200')
        self.title('Denumerator')
        self.table = pd.DataFrame()
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.number = tk.StringVar(value='')
        self.num_entry = ctk.CTkEntry(self, corner_radius=15, height=30, width=400, font=('Kode Mono',18,'bold'),
                                      text_color='green2', placeholder_text='Enter your number here', textvariable=self.number,
                                      placeholder_text_color='green', validate='key',
                                      validatecommand=(self.register(self.is_number), '%P'))
        self.clear_btn = ctk.CTkButton(self,30,30,15, text='x', command=self.clear_entry)
        self.lang_var = tk.StringVar(value='Russian')
        self.language_opt = ctk.CTkOptionMenu(self, values=["Russian", "English"], variable=self.lang_var,
                                              command=self.optionmenu_callback)
        self.scale_var = tk.IntVar(value=1)
        self.short_scale_radio_btn = ctk.CTkRadioButton(self, text="short scale",
                                                        command=self.radiobutton_event, variable=self.scale_var, value=1)
        self.long_scale_radio_btn = ctk.CTkRadioButton(self, text="long scale",
                                                       command=self.radiobutton_event, variable=self.scale_var, value=2)
        self.mode_opt = ctk.CTkOptionMenu(self, values=["Dark mode", "Light mode"], command=self.mode_callback)
        self.mode_opt.grid(row=1, column=3, sticky='w')
        self.language_opt.grid(row=1, column=0, sticky='w',padx=10, pady=10)
        self.short_scale_radio_btn.grid(row=1, column=1, sticky='nsew', pady=10)
        self.long_scale_radio_btn.grid(row=1, column=2, sticky='nsew', pady=10)
        self.clear_btn.grid(row=0,column=3,sticky='w', padx=0, pady=(10,0))
        self.num_entry.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,0), columnspan=3)
        self.tree = ttk.Treeview(self, columns=('num', 'descr'), show='')
        self.tree.column('#1',width=40, stretch=False)
        self.style.configure('Treeview', foreground='#DCE4EE', background='grey20', fieldbackground='grey20')
        self.tree.grid(row=2, column=0, sticky="nsew", columnspan=4, padx=(10,0))
        self.scrollbar = ctk.CTkScrollbar(self,command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=4, sticky="wns", padx=(0,10))
        self.segemented_button_var = ctk.StringVar(value="")
        self.segemented_button = ctk.CTkSegmentedButton(self, values=["Copy as text", "Copy as table", 'Save to file', 'Exit'],
                                                        command=self.segmented_button_callback,
                                                        variable=self.segemented_button_var, corner_radius=6)
        self.segemented_button.grid(row=3, column=0, sticky="nsew", columnspan=5, padx=10, pady=10)
        self.update()
        self.num_entry.focus_set()
    def segmented_button_callback(self, value):
        if value=='Exit': self.destroy()
        elif value=='Copy as text':
            self.clipboard_clear()
            self.clipboard_append(' '.join(self.tree.item(i)['values'][1] for i in self.tree.get_children('')))
        elif value=='Save to file':
            file = filedialog.asksaveasfilename(filetypes=[('MS Excel','*.xlsx'), ('Text Document','*.txt'), ('All files', '*.*')], defaultextension=".xlsx")
            if file and not self.table.empty and file.endswith('xlsx'):
                self.table[['num',0,1,2,'descr']].to_excel(file, index=False)
            elif file and not self.table.empty and file.endswith('txt'):
                with open(file,'w') as txt_file: txt_file.write(self.table['descr'].str.cat(sep=' '))
        elif value=='Copy as table':
            if not self.table.empty: self.table[['num',0,1,2,'descr']].to_clipboard()
        self.after(500, self.segemented_button_var.set, '')
    def clear_entry(self):
        self.number.set('')
        self.num_entry.delete(0,tk.END)
        self.num_entry.after_idle(lambda: self.num_entry.configure(validate='key'))
        self.tree.delete(*self.tree.get_children())
    def optionmenu_callback(self, choice):
        if val:=self.number.get(): self.show_result(val)
    def radiobutton_event(self):
        if val := self.number.get(): self.show_result(val)
    def mode_callback(self, choice):
        bg_color, text_color = {'Dark mode': ['grey20', '#c2d0e1'], 'Light mode':['grey97', 'gray10']}.get(choice)  ## DCE4EE
        ctk.set_appearance_mode(choice.split()[0])
        self.style.configure('Treeview', foreground=text_color, background=bg_color, fieldbackground=bg_color)
    def is_number(self, val):
        if re.fullmatch('[\d,_]{,83}', val):
            val = f'{int(val.replace('_', '')):_d}'
            self.num_entry.delete(0,tk.END)
            self.num_entry.insert(0, val)
            self.num_entry.after_idle(lambda: self.num_entry.configure(validate='key'))
            self.show_result(val)
            return True
        else: return False
    def show_result(self, val):
        self.tree.delete(*self.tree.get_children())
        col = self.lang_var.get()
        scale = f'{col}{self.scale_var.get()}'
        s = pd.Series(val.split('_'))
        df = s.str.extract('(\d(?=\d\d))?([^1])?(\d\d?)').fillna(0).astype('int').pipe(
            lambda df_: df_.set_index(df_.index.sort_values(ascending=False) * 3)).apply(lambda s: pd.Series([s[0] * 100, s[1] * 10, s[2]]), axis=1)
        df_suf = df.apply(lambda s: n[-1] if (n := s[s > 0].tolist()) else 0, axis=1)
        res = (df.
               join(df_nums[col], on=0).
               join(df_nums[col], on=1, rsuffix='d').
               join(df_nums[col], on=2, rsuffix='n').
               join(df_nums[['suf1', 'suf2']], on=df_suf).
               join(df_pow[f'{col}{self.scale_var.get()}']).fillna(''))
        cols = [col, col+'d', col+'n', 'suf1', 'suf2', scale]
        if col == 'Russian':
            if 3 in res.index: res.loc[3] = res.loc[3].replace({'один': 'одна', 'два': 'две'})
            res['descr'] = res[cols].apply(lambda s: s[[col, col+'d', col+'n']].str.cat(sep=' ') + ' ' + (s[scale] +
                                                     (s['suf2'] if s.name <= 3 else s['suf1']) if s[scale] else ''), axis=1)
        else:
            res['descr'] = res[[col, col+'d', col+'n']].apply(lambda s: s[[col,col+'d']].str.cat(sep=' ') +
                                                                        ('-' if s[col+'n'] and s[col+'d'] else ' ') + s[col+'n'], axis=1) + ' ' + res[scale]
        res['num'] = res[[0, 1, 2]].sum(axis=1)
        self.table = res
        for row in res[['num','descr']].query('num>0').itertuples(name='Num'):
            self.tree.insert('', 'end', values=(row.num, re.sub(r'\s+', ' ', row.descr).strip()), tags='_')
        self.tree.tag_configure('_', font=('Kode Mono',10))


if __name__ == '__main__':
    denum = Denum()
    denum.mainloop()

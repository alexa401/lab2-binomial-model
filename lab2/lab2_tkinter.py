"""
Лабораторная работа №2: Ценообразование облигаций со стохастической процентной ставкой
Биномиальная модель (n=10 периодов, T=10 лет)
Вариант 1: t=4 (форвард), k=6 (фьючерс)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math

class BinomialModelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 - Биномиальная модель")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        self.setup_styles()
        self.create_interface()
        self.load_defaults()
        self.calculate_all()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe', background='#2b2b2b', foreground='#ffffff')
        style.configure('TLabelframe.Label', background='#2b2b2b', foreground='#007acc', font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground='#ffffff', padding=5)
    
    def create_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text='Основные расчеты')
        
        self.detail_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_tab, text='Детальный расчет')
        
        self.create_main_tab()
        self.create_detail_tab()
    
    def create_main_tab(self):
        left_frame = ttk.Frame(self.main_tab)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(self.main_tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Параметры
        params_frame = ttk.LabelFrame(left_frame, text="Входные параметры", padding=15)
        params_frame.pack(fill='both', expand=True)
        
        grid_frame = ttk.Frame(params_frame)
        grid_frame.pack(fill='both', expand=True)
        
        params = [
            ('Количество периодов (n):', 'n_var', '10'),
            ('Временной горизонт (T), лет:', 't_var', '10'),
            ('Начальная ставка (r0):', 'r0_var', '0.05'),
            ('Волатильность (sigma):', 'sigma_var', '0.1'),
            ('Номинал облигации:', 'nominal_var', '1.0'),
            ('Период форварда (t):', 'forward_period_var', '4'),
            ('Период фьючерса (k):', 'futures_period_var', '6'),
            ('Страйк 1 (E1):', 'strike1_var', '0.7'),
            ('Страйк 2 (E2):', 'strike2_var', '0.8')
        ]
        
        self.params_vars = {}
        for row, (label_text, var_name, default) in enumerate(params):
            ttk.Label(grid_frame, text=label_text).grid(row=row, column=0, sticky='w', pady=5, padx=5)
            var = tk.StringVar(value=default)
            self.params_vars[var_name] = var
            entry = ttk.Entry(grid_frame, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky='w', pady=5, padx=10)
        
        btn_frame = ttk.Frame(params_frame)
        btn_frame.pack(fill='x', pady=20)
        
        ttk.Button(btn_frame, text="РАССЧИТАТЬ", command=self.calculate_all).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="СБРОСИТЬ", command=self.load_defaults).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="СОХРАНИТЬ", command=self.save_results).pack(side='left', padx=5)
        
        # Результаты
        results_frame = ttk.LabelFrame(right_frame, text="Результаты расчетов", padding=15)
        results_frame.pack(fill='both', expand=True)
        
        self.results_text = tk.Text(results_frame, height=25, width=55, 
                                    bg='#1e1e1e', fg='#d4d4d4', 
                                    font=('Consolas', 10), wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_detail_tab(self):
        self.detail_text = tk.Text(self.detail_tab, bg='#1e1e1e', fg='#d4d4d4', 
                                   font=('Consolas', 9), wrap=tk.WORD)
        self.detail_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.detail_tab, orient='vertical', command=self.detail_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.detail_text.configure(yscrollcommand=scrollbar.set)
    
    def calculate_binomial_params(self, r0, sigma, T, n):
        """Расчет параметров биномиальной модели"""
        dt = T / n
        u = math.exp(sigma * math.sqrt(dt))
        d = 1 / u
        disc = math.exp(r0 * dt)
        p = (disc - d) / (u - d)
        q = 1 - p
        return u, d, p, q, dt
    
    def build_rate_tree(self, r0, u, d, n):
        """Построение дерева процентных ставок"""
        tree = []
        for i in range(n + 1):
            level = []
            for j in range(i + 1):
                rate = r0 * (u ** j) * (d ** (i - j))
                level.append(rate)
            tree.append(level)
        return tree
    
    def compute_zcb_tree(self, r_tree, n, p, q, nominal=1.0):
        """
        Построение дерева цен ZCB обратной индукцией
        """
        zcb_tree = [[0.0] * (i + 1) for i in range(n + 1)]
        
        for j in range(n + 1):
            zcb_tree[n][j] = nominal
        
        for i in range(n - 1, -1, -1):
            for j in range(i + 1):
                zcb_tree[i][j] = (p * zcb_tree[i + 1][j + 1] + q * zcb_tree[i + 1][j]) / (1 + r_tree[i][j])
        
        return zcb_tree
    
    def compute_futures_tree(self, zcb_tree, k, p, q):
        """
        Построение дерева фьючерсных цен (без дисконтирования)
        """
        futures_tree = [[0.0] * (i + 1) for i in range(k + 1)]
        
        for j in range(k + 1):
            futures_tree[k][j] = zcb_tree[k][j]
        
        for i in range(k - 1, -1, -1):
            for j in range(i + 1):
                futures_tree[i][j] = p * futures_tree[i + 1][j + 1] + q * futures_tree[i + 1][j]
        
        return futures_tree
    
    def compute_forward_price(self, zcb_tree, t):
        """Расчет форвардной цены"""
        zcb10 = zcb_tree[0][0]
        zcb_t = zcb_tree[t][0]
        return zcb10 / zcb_t
    
    def compute_european_call(self, futures_tree, r_tree, k, strike, p, q):
        """
        Расчет европейского опциона колл на фьючерс
        Payoff = MAX(Futures_k - strike, 0)
        Затем дисконтирование до момента 0
        """
        option_tree = [[0.0] * (i + 1) for i in range(k + 1)]
        
        # Последний шаг: payoff
        for j in range(k + 1):
            option_tree[k][j] = max(futures_tree[k][j] - strike, 0)
        
        # Обратная индукция с дисконтированием
        for i in range(k - 1, -1, -1):
            for j in range(i + 1):
                option_tree[i][j] = (p * option_tree[i + 1][j + 1] + q * option_tree[i + 1][j]) / (1 + r_tree[i][j])
        
        return option_tree[0][0]
    
    def calculate_all(self):
        """Основной расчет"""
        try:
            n = int(self.params_vars['n_var'].get())
            T = float(self.params_vars['t_var'].get())
            r0 = float(self.params_vars['r0_var'].get())
            sigma = float(self.params_vars['sigma_var'].get())
            nominal = float(self.params_vars['nominal_var'].get())
            t = int(self.params_vars['forward_period_var'].get())
            k = int(self.params_vars['futures_period_var'].get())
            strike1 = float(self.params_vars['strike1_var'].get())
            strike2 = float(self.params_vars['strike2_var'].get())
            
            u, d, p, q, dt = self.calculate_binomial_params(r0, sigma, T, n)
            r_tree = self.build_rate_tree(r0, u, d, n)
            zcb_tree = self.compute_zcb_tree(r_tree, n, p, q, nominal)
            futures_tree = self.compute_futures_tree(zcb_tree, k, p, q)
            
            zcb10 = zcb_tree[0][0]
            forward = self.compute_forward_price(zcb_tree, t)
            futures = futures_tree[0][0]
            call1 = self.compute_european_call(futures_tree, r_tree, k, strike1, p, q)
            call2 = self.compute_european_call(futures_tree, r_tree, k, strike2, p, q)
            
            self.current_params = {
                'n': n, 'T': T, 'r0': r0, 'sigma': sigma, 'nominal': nominal,
                't': t, 'k': k, 'strike1': strike1, 'strike2': strike2,
                'u': u, 'd': d, 'p': p, 'q': q, 'dt': dt,
                'zcb10': zcb10, 'forward': forward, 'futures': futures,
                'call1': call1, 'call2': call2
            }
            
            self.display_results()
            self.display_detail()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете:\n{str(e)}")
    
    def display_results(self):
        p = self.current_params
        
        results = []
        results.append("=" * 60)
        results.append("    ЛАБОРАТОРНАЯ РАБОТА №2")
        results.append("    Биномиальная модель процентной ставки")
        results.append("=" * 60)
        results.append("")
        results.append(f"ВАРИАНТ 1: t={p['t']} (форвард), k={p['k']} (фьючерс)")
        results.append("")
        results.append("ИСХОДНЫЕ ПАРАМЕТРЫ:")
        results.append(f"   n = {p['n']}")
        results.append(f"   T = {p['T']} лет")
        results.append(f"   r0 = {p['r0']*100:.2f}%")
        results.append(f"   sigma = {p['sigma']*100:.2f}%")
        results.append(f"   Номинал = {p['nominal']*100:.0f}%")
        results.append("")
        results.append("ПАРАМЕТРЫ МОДЕЛИ:")
        results.append(f"   u = {p['u']:.6f}")
        results.append(f"   d = {p['d']:.6f}")
        results.append(f"   p = {p['p']:.6f}")
        results.append(f"   q = {p['q']:.6f}")
        results.append(f"   dt = {p['dt']:.4f} лет")
        results.append("")
        results.append("=" * 60)
        results.append("    ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        results.append("=" * 60)
        results.append("")
        results.append(f" 1.  Цена ZCB10:")
        results.append(f"     P(0,10) = {p['zcb10']:.4%}  ({p['zcb10']:.8f})")
        results.append("")
        results.append(f" 2.  Форвардная цена (t={p['t']}):")
        results.append(f"     F_t = {p['forward']:.4%}  ({p['forward']:.8f})")
        results.append("")
        results.append(f" 3.  Фьючерсная цена (k={p['k']}):")
        results.append(f"     Futures_k = {p['futures']:.4%}  ({p['futures']:.8f})")
        results.append("")
        results.append(f" 4.  Европейский опцион колл на фьючерс:")
        results.append(f"     * E = {p['strike1']*100:.0f}%:  C0 = {p['call1']:.4%}  ({p['call1']:.8f})")
        results.append(f"     * E = {p['strike2']*100:.0f}%:  C0 = {p['call2']:.4%}  ({p['call2']:.8f})")
        results.append("")
        results.append("=" * 60)
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, "\n".join(results))
    
    def display_detail(self):
        p = self.current_params
        
        detail = []
        detail.append("=" * 70)
        detail.append(" ДЕТАЛЬНЫЙ РАСЧЕТ")
        detail.append("=" * 70)
        detail.append("")
        detail.append("1. ПАРАМЕТРЫ МОДЕЛИ:")
        detail.append("-" * 70)
        detail.append(f"   dt = T/n = {p['T']}/{p['n']} = {p['dt']:.4f}")
        detail.append(f"   u = exp(σ√dt) = {p['u']:.6f}")
        detail.append(f"   d = 1/u = {p['d']:.6f}")
        detail.append(f"   p = (e^(r·dt)-d)/(u-d) = {p['p']:.6f}")
        detail.append("")
        detail.append("2. ЦЕНА ZCB10:")
        detail.append("-" * 70)
        detail.append(f"   P(0,10) = {p['zcb10']:.8f} = {p['zcb10']:.4%}")
        detail.append("")
        detail.append(f"3. ФОРВАРДНАЯ ЦЕНА (t={p['t']}):")
        detail.append("-" * 70)
        detail.append(f"   F_t = ZCB10 / ZCB_{p['t']} = {p['forward']:.8f} = {p['forward']:.4%}")
        detail.append("")
        detail.append(f"4. ФЬЮЧЕРСНАЯ ЦЕНА (k={p['k']}):")
        detail.append("-" * 70)
        detail.append(f"   Futures_k = {p['futures']:.8f} = {p['futures']:.4%}")
        detail.append("")
        detail.append(f"5. ОПЦИОН КОЛЛ НА ФЬЮЧЕРС (k={p['k']}):")
        detail.append("-" * 70)
        detail.append(f"   Call(E={p['strike1']*100:.0f}%) = {p['call1']:.8f} = {p['call1']:.4%}")
        detail.append(f"   Call(E={p['strike2']*100:.0f}%) = {p['call2']:.8f} = {p['call2']:.4%}")
        detail.append("")
        detail.append("=" * 70)
        
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, "\n".join(detail))
    
    def load_defaults(self):
        self.params_vars['n_var'].set("10")
        self.params_vars['t_var'].set("10")
        self.params_vars['r0_var'].set("0.05")
        self.params_vars['sigma_var'].set("0.1")
        self.params_vars['nominal_var'].set("1.0")
        self.params_vars['forward_period_var'].set("4")
        self.params_vars['futures_period_var'].set("6")
        self.params_vars['strike1_var'].set("0.7")
        self.params_vars['strike2_var'].set("0.8")
        self.calculate_all()
    
    def save_results(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Сохранить результаты"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                    f.write("\n\n")
                    f.write(self.detail_text.get(1.0, tk.END))
                messagebox.showinfo("Успех", f"Результаты сохранены в:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

def main():
    root = tk.Tk()
    app = BinomialModelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
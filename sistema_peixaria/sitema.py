#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface gráfica (Tkinter) - Sistema de Cadastro de Clientes da Peixaria.
Usa o mesmo arquivo 'dados_peixaria.json' da versão de terminal (peixaria.py),,
então os dois programas compartilham os mesmos dados se estiverem na mesma pasta.
"""

import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

ARQUIVO = "dados_peixaria.json"

CATEGORIAS = ["Água doce", "Água salgada", "Crustáceos", "Moluscos", "Outra"]

PEIXES_PADRAO = [
    {"id": 1, "nome": "Tilápia", "categoria": "Água doce", "preco_kg": 24.90},
    {"id": 2, "nome": "Tambaqui", "categoria": "Água doce", "preco_kg": 32.00},
    {"id": 3, "nome": "Pintado", "categoria": "Água doce", "preco_kg": 45.00},
    {"id": 4, "nome": "Serra", "categoria": "Água salgada", "preco_kg": 38.00},
    {"id": 5, "nome": "Cavala", "categoria": "Água salgada", "preco_kg": 28.00},
    {"id": 6, "nome": "Pescada Amarela", "categoria": "Água salgada", "preco_kg": 42.00},
    {"id": 7, "nome": "Tainha", "categoria": "Água salgada", "preco_kg": 22.00},
    {"id": 8, "nome": "Sardinha", "categoria": "Água salgada", "preco_kg": 18.00},
    {"id": 9, "nome": "Robalo", "categoria": "Água salgada", "preco_kg": 55.00},
    {"id": 10, "nome": "Atum", "categoria": "Água salgada", "preco_kg": 60.00},
    {"id": 11, "nome": "Camarão", "categoria": "Crustáceos", "preco_kg": 65.00},
    {"id": 12, "nome": "Lagosta", "categoria": "Crustáceos", "preco_kg": 140.00},
]

COR_TOPO = "#0b4f6c"
COR_DESTAQUE = "#1b85b8"
COR_LINHA = "#eaf4fa"


# ----------------------------------------------------------------------
# Dados
# ----------------------------------------------------------------------
def carregar_dados():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            messagebox.showwarning("Aviso", "Não foi possível ler o arquivo de dados.\nIniciando do zero.")
    return {"peixes": [dict(p) for p in PEIXES_PADRAO], "clientes": []}


def salvar_dados(dados):
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except OSError as e:
        messagebox.showerror("Erro", f"Erro ao salvar os dados:\n{e}")


def proximo_id(lista):
    return max((i["id"] for i in lista), default=0) + 1


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def telefone_valido(tel):
    return len(re.sub(r"\D", "", tel)) in (10, 11)


def formatar_telefone(tel):
    d = re.sub(r"\D", "", tel)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return tel


# ----------------------------------------------------------------------
# Janelas de formulário
# ----------------------------------------------------------------------
class DialogoBase(tk.Toplevel):
    def __init__(self, master, titulo):
        super().__init__(master)
        self.title(titulo)
        self.resizable(False, False)
        self.transient(master)
        self.resultado = None
        self.corpo = ttk.Frame(self, padding=18)
        self.corpo.pack(fill="both", expand=True)
        self.bind("<Escape>", lambda e: self.destroy())

    def botoes(self, linha, texto_ok="Salvar"):
        barra = ttk.Frame(self.corpo)
        barra.grid(row=linha, column=0, columnspan=2, sticky="e", pady=(15, 0))
        ttk.Button(barra, text="Cancelar", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(barra, text=texto_ok, style="Destaque.TButton", command=self.confirmar).pack(side="right")

    def exibir(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.wait_visibility()
        self.grab_set()
        self.wait_window()
        return self.resultado

    def confirmar(self):
        raise NotImplementedError


class DialogoCliente(DialogoBase):
    def __init__(self, master, dados, cliente=None):
        super().__init__(master, "Editar cliente" if cliente else "Novo cliente")
        self.dados = dados
        self.cliente = cliente
        c = self.corpo

        self.var_nome = tk.StringVar(value=cliente["nome"] if cliente else "")
        self.var_tel = tk.StringVar(value=cliente["telefone"] if cliente else "")
        self.var_end = tk.StringVar(value=cliente["endereco"] if cliente else "")

        for i, (rotulo, var) in enumerate(
            [("Nome completo *", self.var_nome), ("Telefone (DDD) *", self.var_tel), ("Endereço", self.var_end)]
        ):
            ttk.Label(c, text=rotulo).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 10))
            ttk.Entry(c, textvariable=var, width=38).grid(row=i, column=1, pady=4)

        ttk.Label(c, text="Peixes preferidos\n(Ctrl/Shift para\nvários)").grid(
            row=3, column=0, sticky="nw", pady=4, padx=(0, 10)
        )
        moldura = ttk.Frame(c)
        moldura.grid(row=3, column=1, pady=4, sticky="w")
        self.lista = tk.Listbox(moldura, selectmode="extended", height=9, width=36, exportselection=False)
        barra = ttk.Scrollbar(moldura, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left")
        barra.pack(side="left", fill="y")

        self.peixes = sorted(dados["peixes"], key=lambda p: p["nome"])
        favoritos = cliente.get("favoritos", []) if cliente else []
        for i, p in enumerate(self.peixes):
            self.lista.insert("end", f"{p['nome']}  ({p['categoria']})")
            if p["id"] in favoritos:
                self.lista.selection_set(i)

        self.botoes(4)
        self.bind("<Return>", lambda e: self.confirmar())

    def confirmar(self):
        nome = self.var_nome.get().strip().title()
        tel = self.var_tel.get().strip()
        if not nome:
            return messagebox.showwarning("Campo obrigatório", "Informe o nome do cliente.", parent=self)
        if not telefone_valido(tel):
            return messagebox.showwarning(
                "Telefone inválido", "Use DDD + número (10 ou 11 dígitos).", parent=self
            )
        self.resultado = {
            "nome": nome,
            "telefone": formatar_telefone(tel),
            "endereco": self.var_end.get().strip(),
            "favoritos": [self.peixes[i]["id"] for i in self.lista.curselection()],
        }
        self.destroy()


class DialogoPeixe(DialogoBase):
    def __init__(self, master, dados, peixe=None):
        super().__init__(master, "Editar peixe" if peixe else "Novo peixe")
        self.dados = dados
        self.peixe = peixe
        c = self.corpo

        self.var_nome = tk.StringVar(value=peixe["nome"] if peixe else "")
        self.var_cat = tk.StringVar(value=peixe["categoria"] if peixe else CATEGORIAS[1])
        self.var_preco = tk.StringVar(value=f"{peixe['preco_kg']:.2f}".replace(".", ",") if peixe else "")

        ttk.Label(c, text="Nome *").grid(row=0, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Entry(c, textvariable=self.var_nome, width=30).grid(row=0, column=1, pady=4)
        ttk.Label(c, text="Categoria").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Combobox(c, textvariable=self.var_cat, values=CATEGORIAS, state="readonly", width=27).grid(
            row=1, column=1, pady=4
        )
        ttk.Label(c, text="Preço por kg (R$) *").grid(row=2, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Entry(c, textvariable=self.var_preco, width=30).grid(row=2, column=1, pady=4)

        self.botoes(3)
        self.bind("<Return>", lambda e: self.confirmar())

    def confirmar(self):
        nome = self.var_nome.get().strip().title()
        if not nome:
            return messagebox.showwarning("Campo obrigatório", "Informe o nome do peixe.", parent=self)
        for p in self.dados["peixes"]:
            if p["nome"].lower() == nome.lower() and p is not self.peixe:
                return messagebox.showwarning("Duplicado", "Esse peixe já está cadastrado.", parent=self)
        try:
            preco = float(self.var_preco.get().strip().replace(",", "."))
            if preco < 0:
                raise ValueError
        except ValueError:
            return messagebox.showwarning("Preço inválido", "Digite um preço válido (ex: 25,90).", parent=self)
        self.resultado = {"nome": nome, "categoria": self.var_cat.get(), "preco_kg": preco}
        self.destroy()


# ----------------------------------------------------------------------
# Aplicação principal
# ----------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Peixaria - Cadastro de Clientes")
        self.geometry("980x600")
        self.minsize(820, 480)
        self.dados = carregar_dados()
        if not os.path.exists(ARQUIVO):
            salvar_dados(self.dados)

        self._estilos()
        self._topo()
        self._abas()
        self._rodape()
        self.atualizar_tudo()

    # ---------- construção ----------
    def _estilos(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Destaque.TButton", background=COR_DESTAQUE, foreground="white", padding=6)
        s.map("Destaque.TButton", background=[("active", COR_TOPO)])
        s.configure("TButton", padding=6)
        s.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=COR_TOPO, foreground="white")
        s.map("Treeview.Heading", background=[("active", COR_DESTAQUE)])
        s.map("Treeview", background=[("selected", COR_DESTAQUE)], foreground=[("selected", "white")])
        s.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 10, "bold"))

    def _topo(self):
        topo = tk.Frame(self, bg=COR_TOPO)
        topo.pack(fill="x")
        tk.Label(
            topo, text="🐟  PEIXARIA", bg=COR_TOPO, fg="white", font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20, pady=12)
        tk.Label(
            topo, text="Sistema de cadastro de clientes", bg=COR_TOPO, fg="#bfe3f4", font=("Segoe UI", 11)
        ).pack(side="left")
        self.lbl_resumo = tk.Label(topo, bg=COR_TOPO, fg="white", font=("Segoe UI", 10))
        self.lbl_resumo.pack(side="right", padx=20)

    def _abas(self):
        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        self._aba_clientes()
        self._aba_peixes()

    def _rodape(self):
        self.var_status = tk.StringVar(value="Pronto.")
        ttk.Label(self, textvariable=self.var_status, relief="sunken", anchor="w", padding=(8, 3)).pack(
            fill="x", side="bottom", pady=(8, 0)
        )

    def _criar_tabela(self, pai, colunas):
        moldura = ttk.Frame(pai)
        moldura.pack(fill="both", expand=True, pady=(8, 0))
        tabela = ttk.Treeview(moldura, columns=[c[0] for c in colunas], show="headings", selectmode="browse")
        for chave, titulo, largura, ancora in colunas:
            tabela.heading(chave, text=titulo)
            tabela.column(chave, width=largura, anchor=ancora, stretch=True)
        barra = ttk.Scrollbar(moldura, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="left", fill="y")
        tabela.tag_configure("par", background=COR_LINHA)
        return tabela

    # ---------- aba de clientes ----------
    def _aba_clientes(self):
        aba = ttk.Frame(self.abas, padding=12)
        self.abas.add(aba, text="👤  Clientes")

        filtros = ttk.Frame(aba)
        filtros.pack(fill="x")
        ttk.Label(filtros, text="Buscar:").pack(side="left")
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *a: self.atualizar_clientes())
        ttk.Entry(filtros, textvariable=self.var_busca, width=28).pack(side="left", padx=(6, 18))
        ttk.Label(filtros, text="Peixe preferido:").pack(side="left")
        self.var_filtro_peixe = tk.StringVar(value="Todos")
        self.cmb_filtro = ttk.Combobox(filtros, textvariable=self.var_filtro_peixe, state="readonly", width=20)
        self.cmb_filtro.pack(side="left", padx=6)
        self.cmb_filtro.bind("<<ComboboxSelected>>", lambda e: self.atualizar_clientes())
        ttk.Button(filtros, text="Limpar filtros", command=self.limpar_filtros).pack(side="left", padx=6)

        self.tab_clientes = self._criar_tabela(
            aba,
            [
                ("id", "ID", 50, "center"),
                ("nome", "Nome", 220, "w"),
                ("telefone", "Telefone", 130, "center"),
                ("endereco", "Endereço", 220, "w"),
                ("favoritos", "Peixes preferidos", 260, "w"),
            ],
        )
        self.tab_clientes.bind("<Double-1>", lambda e: self.editar_cliente())
        self.tab_clientes.bind("<Delete>", lambda e: self.remover_cliente())

        botoes = ttk.Frame(aba)
        botoes.pack(fill="x", pady=(10, 0))
        ttk.Button(botoes, text="➕ Novo cliente", style="Destaque.TButton", command=self.novo_cliente).pack(side="left")
        ttk.Button(botoes, text="✏️ Editar", command=self.editar_cliente).pack(side="left", padx=8)
        ttk.Button(botoes, text="🗑️ Remover", command=self.remover_cliente).pack(side="left")

    # ---------- aba de peixes ----------
    def _aba_peixes(self):
        aba = ttk.Frame(self.abas, padding=12)
        self.abas.add(aba, text="🐠  Tipos de peixes")

        self.tab_peixes = self._criar_tabela(
            aba,
            [
                ("id", "ID", 50, "center"),
                ("nome", "Nome", 240, "w"),
                ("categoria", "Categoria", 180, "w"),
                ("preco", "Preço por kg", 140, "e"),
                ("clientes", "Clientes que preferem", 160, "center"),
            ],
        )
        self.tab_peixes.bind("<Double-1>", lambda e: self.editar_peixe())
        self.tab_peixes.bind("<Delete>", lambda e: self.remover_peixe())

        botoes = ttk.Frame(aba)
        botoes.pack(fill="x", pady=(10, 0))
        ttk.Button(botoes, text="➕ Novo peixe", style="Destaque.TButton", command=self.novo_peixe).pack(side="left")
        ttk.Button(botoes, text="✏️ Editar", command=self.editar_peixe).pack(side="left", padx=8)
        ttk.Button(botoes, text="🗑️ Remover", command=self.remover_peixe).pack(side="left")

    # ---------- atualização das telas ----------
    def atualizar_tudo(self):
        self.atualizar_filtro_peixes()
        self.atualizar_clientes()
        self.atualizar_peixes()

    def atualizar_filtro_peixes(self):
        nomes = ["Todos"] + sorted(p["nome"] for p in self.dados["peixes"])
        self.cmb_filtro["values"] = nomes
        if self.var_filtro_peixe.get() not in nomes:
            self.var_filtro_peixe.set("Todos")

    def limpar_filtros(self):
        self.var_busca.set("")
        self.var_filtro_peixe.set("Todos")
        self.atualizar_clientes()

    def peixe_por_id(self, pid):
        return next((p for p in self.dados["peixes"] if p["id"] == pid), None)

    def nomes_favoritos(self, cliente):
        nomes = [self.peixe_por_id(f)["nome"] for f in cliente.get("favoritos", []) if self.peixe_por_id(f)]
        return ", ".join(nomes) if nomes else "-"

    def atualizar_clientes(self):
        busca = self.var_busca.get().strip().lower()
        busca_num = re.sub(r"\D", "", busca)
        filtro = self.var_filtro_peixe.get()
        peixe_filtro = next((p for p in self.dados["peixes"] if p["nome"] == filtro), None)

        self.tab_clientes.delete(*self.tab_clientes.get_children())
        total = 0
        for c in sorted(self.dados["clientes"], key=lambda x: x["nome"]):
            if busca and busca not in c["nome"].lower() and not (
                busca_num and busca_num in re.sub(r"\D", "", c["telefone"])
            ):
                continue
            if peixe_filtro and peixe_filtro["id"] not in c.get("favoritos", []):
                continue
            tag = ("par",) if total % 2 else ()
            self.tab_clientes.insert(
                "", "end", iid=str(c["id"]), tags=tag,
                values=(c["id"], c["nome"], c["telefone"], c["endereco"] or "-", self.nomes_favoritos(c)),
            )
            total += 1
        self.var_status.set(f"{total} cliente(s) exibido(s) de {len(self.dados['clientes'])}.")
        self._atualizar_resumo()

    def atualizar_peixes(self):
        self.tab_peixes.delete(*self.tab_peixes.get_children())
        for i, p in enumerate(sorted(self.dados["peixes"], key=lambda x: x["nome"])):
            qtd = sum(1 for c in self.dados["clientes"] if p["id"] in c.get("favoritos", []))
            self.tab_peixes.insert(
                "", "end", iid=str(p["id"]), tags=("par",) if i % 2 else (),
                values=(p["id"], p["nome"], p["categoria"], moeda(p["preco_kg"]), qtd),
            )

    def _atualizar_resumo(self):
        self.lbl_resumo.config(
            text=f"{len(self.dados['clientes'])} clientes  |  {len(self.dados['peixes'])} tipos de peixe"
        )

    # ---------- ações: clientes ----------
    def _cliente_selecionado(self):
        sel = self.tab_clientes.selection()
        if not sel:
            messagebox.showinfo("Selecione", "Selecione um cliente na lista.")
            return None
        return next((c for c in self.dados["clientes"] if c["id"] == int(sel[0])), None)

    def novo_cliente(self):
        r = DialogoCliente(self, self.dados).exibir()
        if r:
            r["id"] = proximo_id(self.dados["clientes"])
            self.dados["clientes"].append(r)
            salvar_dados(self.dados)
            self.atualizar_clientes()
            self.atualizar_peixes()
            self.var_status.set(f"Cliente '{r['nome']}' cadastrado.")

    def editar_cliente(self):
        c = self._cliente_selecionado()
        if not c:
            return
        r = DialogoCliente(self, self.dados, c).exibir()
        if r:
            c.update(r)
            salvar_dados(self.dados)
            self.atualizar_clientes()
            self.atualizar_peixes()
            self.var_status.set(f"Cliente '{c['nome']}' atualizado.")

    def remover_cliente(self):
        c = self._cliente_selecionado()
        if c and messagebox.askyesno("Remover", f"Remover o cliente '{c['nome']}'?"):
            self.dados["clientes"].remove(c)
            salvar_dados(self.dados)
            self.atualizar_clientes()
            self.atualizar_peixes()
            self.var_status.set(f"Cliente '{c['nome']}' removido.")

    # ---------- ações: peixes ----------
    def _peixe_selecionado(self):
        sel = self.tab_peixes.selection()
        if not sel:
            messagebox.showinfo("Selecione", "Selecione um peixe na lista.")
            return None
        return self.peixe_por_id(int(sel[0]))

    def novo_peixe(self):
        r = DialogoPeixe(self, self.dados).exibir()
        if r:
            r["id"] = proximo_id(self.dados["peixes"])
            self.dados["peixes"].append(r)
            salvar_dados(self.dados)
            self.atualizar_tudo()
            self.var_status.set(f"Peixe '{r['nome']}' cadastrado.")

    def editar_peixe(self):
        p = self._peixe_selecionado()
        if not p:
            return
        r = DialogoPeixe(self, self.dados, p).exibir()
        if r:
            p.update(r)
            salvar_dados(self.dados)
            self.atualizar_tudo()
            self.var_status.set(f"Peixe '{p['nome']}' atualizado.")

    def remover_peixe(self):
        p = self._peixe_selecionado()
        if p and messagebox.askyesno(
            "Remover", f"Remover '{p['nome']}'?\nEle também sairá dos peixes preferidos dos clientes."
        ):
            self.dados["peixes"].remove(p)
            for c in self.dados["clientes"]:
                c["favoritos"] = [f for f in c.get("favoritos", []) if f != p["id"]]
            salvar_dados(self.dados)
            self.atualizar_tudo()
            self.var_status.set(f"Peixe '{p['nome']}' removido.")


if __name__ == "__main__":
    App().mainloop()

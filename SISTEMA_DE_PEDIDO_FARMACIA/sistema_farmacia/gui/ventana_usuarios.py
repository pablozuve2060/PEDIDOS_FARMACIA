import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL
from services import persistencia

ROLES_DISPONIBLES = ("admin", "vendedor")


class VentanaUsuarios(tb.Toplevel):

    def __init__(self, parent, usuario_actual, al_cerrar=None):
        super().__init__(parent)
        self.title("Gestión de Usuarios")
        aplicar_favicon(self)
        self.usuario_actual = usuario_actual
        self.al_cerrar = al_cerrar
        self.usuario_seleccionado = None
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._construir_ui()
        self._refrescar_tabla()
        centrar_ventana(self, 640, 540)

    def _construir_ui(self):
        tb.Label(self, text="👥 Gestión de Usuarios", font=FUENTE_TITULO).pack(
            pady=(15, 10)
        )
        form = tb.Frame(self, padding=10)
        form.pack(fill="x", padx=15)
        tb.Label(form, text="Usuario", font=FUENTE_NORMAL).grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.entry_usuario = tb.Entry(form, width=20)
        self.entry_usuario.grid(row=1, column=0, padx=5, pady=(0, 8))
        tb.Label(form, text="Nombre completo", font=FUENTE_NORMAL).grid(
            row=0, column=1, sticky="w", padx=5
        )
        self.entry_nombre = tb.Entry(form, width=22)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=(0, 8))
        tb.Label(form, text="Rol", font=FUENTE_NORMAL).grid(
            row=0, column=2, sticky="w", padx=5
        )
        self.combo_rol = tb.Combobox(
            form, values=ROLES_DISPONIBLES, width=15, state="readonly"
        )
        self.combo_rol.current(1)
        self.combo_rol.grid(row=1, column=2, padx=5, pady=(0, 8))
        tb.Label(
            form,
            text="Contraseña (dejar vacío para no cambiarla al actualizar)",
            font=FUENTE_NORMAL,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
        self.entry_clave = tb.Entry(form, width=20, show="•")
        self.entry_clave.grid(row=3, column=0, padx=5, pady=(0, 8))
        botones_form = tb.Frame(self)
        botones_form.pack(fill="x", padx=15, pady=(5, 10))
        tb.Button(
            botones_form,
            text="➕ Crear",
            bootstyle="success",
            command=self._crear,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="✏️ Actualizar",
            bootstyle="warning",
            command=self._actualizar,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="🗑️ Eliminar",
            bootstyle="danger",
            command=self._eliminar,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="🧹 Limpiar",
            bootstyle="secondary",
            command=self._limpiar_formulario,
        ).pack(side="left", padx=5)
        tb.Separator(self).pack(fill="x", padx=15, pady=5)
        self.tabla = tb.Treeview(
            self,
            columns=("usuario", "nombre", "rol"),
            show="headings",
            bootstyle="primary",
            height=12,
        )
        for col, txt, w in [
            ("usuario", "Usuario", 150),
            ("nombre", "Nombre", 240),
            ("rol", "Rol", 120),
        ]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for u in persistencia.cargar_usuarios():
            self.tabla.insert("", "end", values=(u["usuario"], u["nombre"], u["rol"]))

    def _al_seleccionar_fila(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0])["values"]
        self.usuario_seleccionado = str(valores[0])
        self.entry_usuario.delete(0, "end")
        self.entry_usuario.insert(0, valores[0])
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, valores[1])
        self.combo_rol.set(valores[2])
        self.entry_clave.delete(0, "end")

    def _limpiar_formulario(self):
        self.entry_usuario.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_clave.delete(0, "end")
        self.combo_rol.current(1)
        self.usuario_seleccionado = None
        self.tabla.selection_remove(self.tabla.selection())

    def _crear(self):
        usuario = self.entry_usuario.get().strip()
        nombre = self.entry_nombre.get().strip()
        rol = self.combo_rol.get().strip()
        clave = self.entry_clave.get().strip()
        if not usuario or not nombre or not clave:
            messagebox.showwarning(
                "Datos incompletos", "Usuario, nombre y contraseña son obligatorios."
            )
            return
        if persistencia.crear_usuario(usuario, clave, rol, nombre):
            messagebox.showinfo("Éxito", "Usuario creado correctamente.")
            self._refrescar_tabla()
            self._limpiar_formulario()
        else:
            messagebox.showwarning("Duplicado", f"Ya existe un usuario '{usuario}'.")

    def _actualizar(self):
        if not self.usuario_seleccionado:
            messagebox.showwarning(
                "Sin selección", "Selecciona un usuario de la tabla."
            )
            return
        nombre = self.entry_nombre.get().strip()
        rol = self.combo_rol.get().strip()
        clave = self.entry_clave.get().strip() or None
        if not nombre:
            messagebox.showwarning("Datos incompletos", "El nombre es obligatorio.")
            return
        if self.usuario_seleccionado == self.usuario_actual["usuario"] and rol != "admin":
            messagebox.showwarning(
                "Operación no permitida",
                "No puedes quitarte tu propio rol de administrador.",
            )
            return
        persistencia.actualizar_usuario(
            self.usuario_seleccionado, nueva_clave=clave, rol=rol, nombre=nombre
        )
        messagebox.showinfo("Éxito", "Usuario actualizado.")
        self._refrescar_tabla()
        self._limpiar_formulario()

    def _eliminar(self):
        if not self.usuario_seleccionado:
            messagebox.showwarning(
                "Sin selección", "Selecciona un usuario de la tabla."
            )
            return
        if self.usuario_seleccionado == self.usuario_actual["usuario"]:
            messagebox.showwarning(
                "Operación no permitida", "No puedes eliminar tu propio usuario."
            )
            return
        if not messagebox.askyesno(
            "Confirmar", f"¿Eliminar al usuario '{self.usuario_seleccionado}'?"
        ):
            return
        persistencia.eliminar_usuario(self.usuario_seleccionado)
        self._refrescar_tabla()
        self._limpiar_formulario()

    def _cerrar(self):
        if self.al_cerrar:
            self.al_cerrar()
        self.destroy()

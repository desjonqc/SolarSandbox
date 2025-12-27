from math import atan2, degrees
from tkinter import *

import numpy as np
from PIL import Image, ImageTk
from customtkinter import CTkButton, CTkScrollableFrame, CTk, CTkLabel, CTkSlider, CTkComboBox

from physics import configs
from physics.solarsandbox import CelestialBody, SolarSystem, Star, Planet
from physics.solver import SimulationSolver
from utils import constants


def convert_rbg_hex(rgb):
    r, g, b = rgb
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


class DragTracker:
    def __init__(self, canvas):
        self.canvas = canvas
        self.start_x = None
        self.start_y = None
        self.total_dx = 0
        self.total_dy = 0

    def on_button_press(self, event):
        # Capture la position initiale
        self.start_x, self.start_y = event.x, event.y
        self.canvas.scan_mark(event.x, event.y)

    def on_drag(self, event):
        # Met à jour la vue avec scan_dragto
        self.canvas.scan_dragto(event.x, event.y, gain=1)

        # Calcule le déplacement en pixels
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        # Met à jour les positions pour le prochain calcul
        self.start_x, self.start_y = event.x, event.y

        # Cumul des déplacements
        self.total_dx += dx
        self.total_dy += dy

    def convert_canvas_coords(self, x, y):
        return x - self.total_dx, y - self.total_dy

    def reset(self):
        self.total_dx = 0
        self.total_dy = 0


class WidgetHandler:
    def __init__(self):
        self.__custom_widgets_class = []
        self._widgets = []

    def add_widget(self, widget):
        self.__custom_widgets_class.append(widget)

    def initialize_widgets(self, tk_parent, parent_window):
        for widget_class in self.__custom_widgets_class:
            widget = widget_class(tk_parent, parent_window)
            self._widgets.append(widget)
            widget.initialize_widget(self)

    def get_widget(self, widget_class):
        for widget in self._widgets:
            if isinstance(widget, widget_class):
                return widget
        return None


class UI(WidgetHandler):
    def __init__(self, title, window):
        super().__init__()
        self.title = title
        self.window = window
        self._children = {}

    def add_child(self, child):
        self._children[type(child)] = child

    def initialize_window(self):
        self.window.title(self.title)
        self.initialize_widgets(self.window, self)

    def display_child(self, child_class):
        self._children[child_class].initialize_window()

    def start_loop(self):
        self.window.mainloop()


class SolarSystemWindow(UI):
    def __init__(self, solar_system: SolarSystem, speed=1):
        super().__init__("Système solaire", CTk())
        self.solar_system = solar_system
        self.speed = speed
        self.simulation = SimulationSolver(solar_system)
        self.add_widget(LeftFrame)
        self.add_widget(SolarCanvasWidget)
        # self.add_child(SettingsWindow(self))
        self.simulation_pause = False

        self.initialize_window()
        self.start_loop()

    def initialize_window(self):
        super().initialize_window()

        # Passage en plein écran :
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        self.window.geometry(f"{width}x{height} + 0 + 0")
        # self.window.attributes("-fullscreen", True)
        self.window.after(10, lambda: self.window.geometry(f"{width}x{height} + 0 + 0"))

        # Changement du fond d'écran
        self.window.config(bg="#00203A")

        self.window.bind("<Delete>", lambda e: self.get_widget(LeftFrame).get_widget(InfoFrame).remove_selected_body())

    def update_components(self):
        for widget in self._widgets:
            widget.update_widget()
        """
        Met à jour les composants de la fenêtre lorsque la simulation avance.
        """

    def update_simulation(self):
        if not self.simulation_pause:
            self.simulation.solve_step()
            self.update_components()
        self.window.after(self.speed, self.update_simulation)

    def start_loop(self):
        self.update_simulation()
        super().start_loop()


class SettingsWindow(UI):
    def __init__(self, parent: SolarSystemWindow):
        super().__init__("Paramètres", Toplevel(parent.window))
        self.parent = parent

    def initialize_window(self):
        super().initialize_window()

        self.window.geometry("400x400")


class CustomWidget(WidgetHandler):
    def __init__(self, tk_parent, parent_window):
        super().__init__()
        """
        Widget personnalisé (Un bouton, un label, etc.). Doit être ajouté à une fenêtre parente.
        Permet de gérer proprement des widgets complexes.

        :param tk_window: La fenêtre tk, par exemple tk_window = parent_window.window
        :param parent_window: L'objet gérant la fenêtre du parent
        """
        self.tk_parent = tk_parent
        self.parent_window = parent_window

    def initialize_widget(self, handler):
        """
        Initialise le widget, en l'ajoutant à la fenêtre tk_window et en donnant ses propriétés.
        :param handler:
        """
        self.initialize_widgets(self.tk_parent, self.parent_window)

    def update_widget(self):
        """
        Met à jour le widget lorsque la résolution fait un pas.
        """
        pass


class FrameWidget(CustomWidget):
    def __init__(self, tk_parent, parent_window: UI):
        super().__init__(tk_parent, parent_window)
        self.frame = Frame(tk_parent)

    def initialize_widget(self, handler):
        self.initialize_widgets(self.frame, self.parent_window)

    def update_widget(self):
        pass


class ScrollFrameWidget(CustomWidget):
    def __init__(self, tk_parent, parent_window: UI):
        super().__init__(tk_parent, parent_window)
        self.frame = CTkScrollableFrame(tk_parent, bg_color="#F6B12D", fg_color="#F6B12D")

    def initialize_widget(self, handler):
        self.initialize_widgets(self.frame, self.parent_window)

    def update_widget(self):
        pass


class LeftFrame(FrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.frame.config(bg="#F6B12D", width=300)
        self.add_widget(InfoFrame)
        self.add_widget(ControlFrame)
        self.add_widget(ConfigFrame)
        self.add_widget(ScaleFrame)
        self.add_widget(PauseFrame)

    def initialize_widget(self, handler):
        super().initialize_widget(handler)
        self.frame.pack(side=LEFT, fill=Y)


class ControlFrame(ScrollFrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.buttons = {}
        self.handler = None
        self.new_button = None  # Bouton pour ajouter un nouvel astre

    def initialize_widget(self, handler):
        self.handler = handler
        super().initialize_widget(handler)
        self.frame.config(bg="#F6B12D", padx=10, pady=10)
        self.frame.pack(fill=BOTH, expand=True)

        # Ajouter le bouton "New"
        self.new_button = CTkButton(
            self.frame,
            text="New",
            fg_color="#28a745",
            command=self.create_new_body
        )
        self.new_button.pack(fill=X, pady=5)

        self.update()

    # on crée les boutons correspondant aux planètes

    def update(self):
        info_frame = self.handler.get_widget(InfoFrame)
        def click_event(body):
            distance_from_center = body.get_distance_from(
                self.parent_window.solar_system.get_center_of_mass(self.parent_window.solar_system.bodies()))
            if self.parent_window.get_widget(SolarCanvasWidget).scale_au() * constants.AU < distance_from_center:
                self.handler.get_widget(ScaleFrame).apply_scale(int(min(700, distance_from_center * 21 / constants.AU)))
            info_frame.show_details(
                body if body != info_frame.selected_body else None)
        for body in self.parent_window.solar_system.bodies():
            if body not in self.buttons:
                btn = CTkButton(
                    self.frame,
                    text=body.name,
                    corner_radius=50,
                    command=lambda const_body=body: click_event(const_body), hover_color="red",
                    width=100,
                    fg_color="#F26619",
                )
                btn.bind("<Button-3>", lambda e, name=body: info_frame.modify(name))
                btn.pack(pady=4, padx=10, fill=BOTH, expand=True)
                self.buttons[body] = btn

    def remove_body(self, body):
        self.buttons[body].destroy()
        del self.buttons[body]

    def create_new_body(self):
        # Afficher une fenêtre pour créer un nouvel astre
        self.show_add_body_window()

    def show_add_body_window(self):
        # Fenêtre contextuelle pour ajouter un astre
        selected_body = self.handler.get_widget(InfoFrame).selected_body

        new_window = Toplevel(self.frame)
        new_window.title("Ajouter un nouvel astre")
        new_window.geometry("300x475")
        new_window.config(bg="#00203A")

        Label(new_window, text="Name:", bg="#00203A", fg="white").pack(pady=5)
        name_entry = Entry(new_window)
        name_entry.pack(pady=5)

        Label(new_window, text="Weight (kg):", bg="#00203A", fg="white").pack(pady=5)
        mass_entry = Entry(new_window)
        mass_entry.pack(pady=5)

        Label(new_window, text="Radius (m):", bg="#00203A", fg="white").pack(pady=5)
        radius_entry = Entry(new_window)
        radius_entry.pack(pady=5)

        Label(new_window, text="Position (x, y) (m):" if selected_body is None else "Semi-major axis:", bg="#00203A",
              fg="white").pack(pady=5)
        position_entry = Entry(new_window)
        position_entry.pack(pady=5)

        Label(new_window, text="Speed (vx, vy) (m/s):" if selected_body is None else "Trajectory radius:",
              bg="#00203A", fg="white").pack(pady=5)
        velocity_entry = Entry(new_window)
        velocity_entry.pack(pady=5)

        Label(new_window, text="Type of celestial body (star/planet):", bg="#00203A", fg="white").pack(pady=5)
        values = ["Default", "Star", "Planet"]
        type_entry = CTkComboBox(new_window, values=values)
        type_entry.pack(pady=5)

        def add_body():
            try:
                name = name_entry.get()
                mass = float(mass_entry.get())
                radius = float(radius_entry.get())
                if selected_body is None:
                    position = tuple(map(float, position_entry.get().split(',')))
                    velocity = tuple(map(float, velocity_entry.get().split(',')))
                else:
                    position = np.array(
                        [float(velocity_entry.get()), 0]) + selected_body.position
                    velocity = np.array(
                        [0, SolarSystem.convert_speed(float(velocity_entry.get()), float(position_entry.get()), selected_body.mass)]) + selected_body.velocity
                body_type = type_entry.get()

                # Si aucune valeur n'est entrée pour le type, on définit "corps céleste par défaut"

                # Créer un nouveau corps céleste avec le type spécifié
                if body_type == "Default":
                    new_body = CelestialBody(name, mass, radius, np.array(position), np.array(velocity), None)
                elif body_type == "Planet":
                    new_body = Planet(name, mass, radius, np.array(position), np.array(velocity), 0.3, "H2", None)
                else:
                    new_body = Star(name, mass, radius, np.array(position), np.array(velocity), 5000, None)
                new_body.body_type = body_type  # Assigner le type au corps céleste

                # Ajouter le corps au système
                self.parent_window.solar_system.add_body(new_body)
                self.update()
                new_window.destroy()
            except Exception as e:
                print("Error during the creation of the celestial body:", e)

        # Bouton pour valider l'ajout
        CTkButton(new_window, text="Add", command=add_body, fg_color="#28a745").pack(pady=10)

        # Bouton pour fermer la fenêtre
        CTkButton(new_window, text="Cancel", command=new_window.destroy, fg_color="#dc3545").pack(pady=5)


class SolarCanvasWidget(CustomWidget):
    def __init__(self, parent, solar_system_ui: SolarSystemWindow):
        super().__init__(parent, solar_system_ui)
        self.canvas = Canvas(self.tk_parent, bg="#00073c", highlightthickness=0)
        self.drag_tracker = DragTracker(self.canvas)
        self.radius_scale = 1 / 1600
        self.image_tk = None

        self.handler = None
        self.scale = 1
        self.shadow = False

    def initialize_widget(self, handler):
        self.handler = handler
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=True)
        self.set_scale(12)
        # image = Image.open("./assets/fond3.jpg")
        # image = image.resize((self.canvas.winfo_screenwidth(), self.canvas.winfo_screenheight()))
        # self.image_tk = ImageTk.PhotoImage(image)
        # self.canvas.create_image(0,0, anchor = NW, image = self.image_tk)
        self.update_widget()
        self.bind_click_events()
        self.bind_drag_events()

    def set_scale(self, ua):
        self.scale = self.canvas.winfo_screenheight() / (ua * constants.AU)

    def scale_au(self):
        return self.canvas.winfo_screenheight() / (self.scale * constants.AU)

    def max_radius(self):
        return min(50, 35 * np.exp(-self.scale_au() / 3) + 5)

    def draw_body(self, body):

        x, y = self.parent_window.solar_system.convert_coords(body.position, self.canvas.winfo_screenwidth(),
                                                              self.canvas.winfo_screenheight(), self.scale)
        if hasattr(body.graphics, 'light_sides'):
            for arc in body.graphics.light_sides:
                self.canvas.delete(arc)  # Supprimer les arcs précédents
        else:
            body.graphics.light_sides = []

        if body.graphics.has_to_draw_trajectory():
            x0, y0 = self.parent_window.solar_system.convert_coords(body.position_cache[69],
                                                                    self.canvas.winfo_screenwidth(),
                                                                    self.canvas.winfo_screenheight(), self.scale)
            body.graphics.add_trajectory(self.canvas.create_line(x, y, x0, y0, fill="white"))

        if body.graphics.canvas_object is not None:
            self.canvas.delete(body.graphics.canvas_object)

        r = min(self.max_radius(), body.radius * self.radius_scale)

        astre_color = convert_rbg_hex(body.get_color(self.parent_window.solar_system))
        factor = 0.4

        couleur_assombrie = "#{:02X}{:02X}{:02X}".format(
            *[int(int(astre_color[i:i + 2], 16) * factor) for i in (1, 3, 5)]) if self.shadow else astre_color

        if isinstance(body, Star):
            body.graphics.attach_canvas_object(self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                                                       fill=astre_color,
                                                                       outline=""))
        else:
            body.graphics.attach_canvas_object(self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                                                       fill=couleur_assombrie,
                                                                       outline=""))

        if body.graphics.has_to_pop_trajectory():
            self.canvas.delete(body.graphics.pop_trajectory())

        if self.shadow and not isinstance(body, Star):
            liste_of_stars = [bodybis for bodybis in self.parent_window.solar_system.bodies() if
                              isinstance(bodybis, Star)]
            # print(liste_of_stars)
            for star in liste_of_stars:
                self.draw_light_side(body, star, x, y, r)

    # Calcule la couleur moyenne entre deux couleurs (format hexadécimal)

    def draw_light_side(self, body, star, x, y, r):
        # Coordonnées de l'étoile que je prends comme source de lumière
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        star_x, star_y = self.parent_window.solar_system.convert_coords(
            star.position, canvas_width, canvas_height, self.scale
        )
        # print(f"Planet: ({x}, {y}), Star: ({star_x}, {star_y}), Radius: {r}")

        # angle de l'éclairage
        angle = atan2(star_y - y, star_x - x)

        body_color = convert_rbg_hex(body.get_color(self.parent_window.solar_system))
        blanc = "#FFFFFF"
        start_angle = - 90 - degrees(angle)

        light_color = "#{:02X}{:02X}{:02X}".format(
            *[(int(blanc[i:i + 2], 16) + int(body_color[i:i + 2], 16)) // 2 for i in (1, 3, 5)])

        # Dessine le demi-cercle blanc
        arc = self.canvas.create_arc(
            x - r, y - r, x + r, y + r,
            start=start_angle, extent=180,
            fill=light_color, outline=""
        )

        body.graphics.light_sides.append(arc)

    def clear_trajectories(self):
        for body in self.parent_window.solar_system.bodies():
            for trajectory in body.graphics.trajectory_objects:
                self.canvas.delete(trajectory)
            body.graphics.trajectory_objects = []

    def update_widget(self):
        self.parent_window.get_widget(LeftFrame).get_widget(InfoFrame).update_description()
        bodies = self.parent_window.solar_system.bodies()
        dx, dy = np.array((self.drag_tracker.total_dx, self.drag_tracker.total_dy), dtype=float) / self.scale
        meter_scale = self.canvas.winfo_screenheight() / self.scale
        for body in bodies:
            if np.linalg.norm(body.position + np.array((dx, dy))) <= 1.7 * meter_scale:
                self.draw_body(body)
            else:
                if body.graphics.canvas_object is not None:
                    self.canvas.delete(body.graphics.canvas_object)
                for trajectory in body.graphics.trajectory_objects:
                    self.canvas.delete(trajectory)
                body.graphics.trajectory_objects = []
                for light in body.graphics.light_sides:
                    self.canvas.delete(light)
                body.graphics.light_sides = []

    def remove_body(self, body):
        self.canvas.delete(body.graphics.canvas_object)
        for arc in body.graphics.light_sides:
            self.canvas.delete(arc)
        self.clear_trajectories()

    def bind_drag_events(self):
        self.canvas.bind("<B1-Motion>", self.drag_tracker.on_drag)

    def reset_drag_position(self):
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.drag_tracker.reset()

    def bind_click_events(self):
        def afficher_nom(event, left_click):
            if left_click:
                self.drag_tracker.on_button_press(event)

            width, height = self.canvas.winfo_screenwidth(), self.canvas.winfo_screenheight()
            x, y = self.drag_tracker.convert_canvas_coords(event.x, event.y)
            for body in self.parent_window.solar_system.bodies():
                body_x, body_y = self.parent_window.solar_system.convert_coords(body.position,
                                                                                width,
                                                                                height,
                                                                                self.scale)
                radius = max(min(self.max_radius(), body.radius * self.radius_scale), 5)

                distance = np.sqrt((x - body_x) ** 2 + (y - body_y) ** 2)

                if distance <= radius:
                    info_frame = self.handler.get_widget(LeftFrame).get_widget(InfoFrame)
                    if left_click:
                        if info_frame.selected_body != body:
                            info_frame.show_details(body)
                            self.draw_body(body)
                        else:
                            info_frame.show_details(None)
                    else:
                        info_frame.modify(body)
                    return

        self.canvas.bind("<Button-1>", lambda event: afficher_nom(event, True))
        self.canvas.bind("<Button-3>", lambda event: afficher_nom(event, False))


class InfoFrame(FrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.info_label = Label(self.frame, text="", bg="#F6B12D", anchor="w", justify="left",
                                font=("Arial", 30, 'bold'))
        self.entries = []
        self.body_canvas = Canvas(self.frame, width=400, height=280, bg="#00073c", highlightthickness=0)
        image = Image.open("./assets/fond3.jpg")
        image = image.resize((620, 280))
        self.image_tk = ImageTk.PhotoImage(image)
        self.body_canvas.create_image(0, 0, anchor=NW, image=self.image_tk)

        self.selected_body = None
        self.photo_tk = None

    def initialize_widget(self, handler):
        super().initialize_widget(handler)
        self.frame.config(bg="#F6B12D", height=200, padx=10, pady=10)
        self.frame.pack(fill=X, padx=10, pady=10)
        self.info_label.pack(fill=BOTH, expand=True)
        self.body_canvas.pack(fill=X)

    def show_body(self, body):
        self.selected_body = body
        self.body_canvas.delete("all")
        if body is not None:
            self.body_canvas.create_image(0, 0, anchor=NW, image=self.image_tk)
            width = self.body_canvas.winfo_width()
            height = self.body_canvas.winfo_height()
            radius = 0.4 * height
            x1 = 0.5 * width - radius
            y1 = 0.1 * height
            x2 = x1 + 2 * radius
            y2 = y1 + 2 * radius

            color_hex = convert_rbg_hex(body.get_color(self.parent_window.solar_system))

            if body.photo is None:
                self.body_canvas.create_oval(x1, y1, x2, y2, fill=color_hex, outline=color_hex)
            else:
                photo = Image.open(body.photo)
                photo = photo.resize((280, 280))
                self.photo_tk = ImageTk.PhotoImage(photo)
                self.body_canvas.tag_raise(self.body_canvas.create_image(170, 0, anchor=NW, image=self.photo_tk))

    def show_details(self, body):
        self.reset_entries()
        self.show_body(body)
        self.update_description()

    def update_description(self):
        if self.selected_body is not None:
            self.info_label.config(text=self.selected_body.get_info(self.parent_window.solar_system))
        else:
            self.info_label.config(text="")

    def reset_entries(self):
        for entry in self.entries:
            entry.destroy()
        self.entries = []

    def modify(self, body):
        self.show_details(None)

        self.show_body(body)
        self.entries = body.get_entries(self.frame,
                                        lambda: self.parent_window.get_widget(SolarCanvasWidget).clear_trajectories())
        for entry in self.entries:
            entry.pack(fill=X, pady=2)

    def remove_selected_body(self):
        if self.selected_body is not None:
            self.parent_window.get_widget(SolarCanvasWidget).remove_body(self.selected_body)
            self.parent_window.get_widget(LeftFrame).get_widget(ControlFrame).remove_body(self.selected_body)
            self.parent_window.solar_system.remove_body(self.selected_body)
            self.show_details(None)
            self.body_canvas.create_image(0, 0, anchor=NW, image=self.image_tk)


class PauseFrame(FrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.frame.config(bg="#F6B12D", width=300)
        self.pause_button = CTkButton(self.frame, text="Pause", command=self.toggle_pause, fg_color="#F26619",
                                      bg_color="#F6B12D", corner_radius=15)
        self.shadow_button = CTkButton(self.frame, text="Shadows", command=self.toggle_shadow, fg_color="#F26619",
                                       bg_color="#F6B12D", corner_radius=15)

    def initialize_widget(self, handler):
        super().initialize_widget(handler)
        self.frame.pack(fill=X)
        self.pause_button.pack(fill=BOTH, padx=10, pady=10)
        self.shadow_button.pack(fill=BOTH, padx=10, pady=10)

    def toggle_pause(self):
        self.parent_window.simulation_pause = not self.parent_window.simulation_pause
        if self.parent_window.simulation_pause:
            self.pause_button.config(text="Play")
        else:
            self.pause_button.config(text="Pause")

    def toggle_shadow(self):
        self.parent_window.get_widget(SolarCanvasWidget).shadow = not self.parent_window.get_widget(
            SolarCanvasWidget).shadow
        if self.parent_window.get_widget(SolarCanvasWidget).shadow:
            self.shadow_button.config(text="No shadows")
        else:
            self.shadow_button.config(text="Shadows")


class ScaleFrame(FrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.frame.config(bg="#F6B12D", width=300)
        self.scale_label = CTkLabel(self.frame, text="Scale : (UA)", fg_color="#F26619", bg_color="#F6B12D")
        self.scale_slider = CTkSlider(self.frame, from_=1, to=700, command=self.apply_scale, fg_color="#F26619",
                                      bg_color="#F6B12D", border_color="#F6B12D")
        self.scale_slider.set(120)
        self.reset_button = CTkButton(self.frame, text="Reset", command=self.reset, fg_color="#F26619",
                                      bg_color="#F6B12D")
        self.handler = None

    def initialize_widget(self, handler):
        self.handler = handler
        super().initialize_widget(handler)
        self.frame.pack(fill=X)
        self.scale_label.pack(side=LEFT)
        self.reset_button.pack(side=RIGHT)
        self.scale_slider.pack(side=RIGHT)

    def apply_scale(self, value):
        widget = self.parent_window.get_widget(SolarCanvasWidget)
        widget.set_scale(value / 10)
        widget.clear_trajectories()

    def reset(self):
        self.scale_slider.set(120)
        self.apply_scale(12)
        self.parent_window.get_widget(SolarCanvasWidget).reset_drag_position()


class ConfigFrame(FrameWidget):
    def __init__(self, tk_parent, parent_window):
        super().__init__(tk_parent, parent_window)
        self.frame.config(bg="#F6B12D", width=300)
        self.config_label = CTkLabel(self.frame, text="Configuration", fg_color="#F26619", bg_color="#F6B12D")
        self.data = configs.CONFIGURATIONS

        self.config_list = CTkComboBox(self.frame, fg_color="#F26619", bg_color="#F6B12D",
                                       values=list(self.data.keys()), command=self.change_config)

        self.handler = None

    def initialize_widget(self, handler):
        self.handler = handler
        super().initialize_widget(handler)
        self.frame.pack(fill=X)
        self.config_label.pack(side=LEFT, fill=X)
        self.frame.config(bg="#F6B12D", width=300)
        self.config_list.pack(side=RIGHT)

    def change_config(self, event):
        config = self.config_list.get()
        for body in self.parent_window.solar_system.bodies():
            self.parent_window.get_widget(SolarCanvasWidget).remove_body(body)
            self.parent_window.get_widget(LeftFrame).get_widget(ControlFrame).remove_body(body)
        self.parent_window.solar_system.bodies().clear()

        for body in configs.clone(self.data[config]):
            self.parent_window.solar_system.add_body(body)
        self.handler.get_widget(ControlFrame).update()

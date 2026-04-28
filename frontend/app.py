import flet as ft
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime

# ================= CONFIG =================
DB_NAME = "freelance"
DB_USER = "freelance_user"
DB_PASS = "freelance123"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

BG = "https://images.unsplash.com/photo-1492724441997-5dc865305da7"


# ================= DB =================
def get_conn():
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
    except OperationalError as e:
        print("❌ DB Error:", e)
        return None


def init_db():
    conn = get_conn()
    if conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS persons(
                    id SERIAL PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT,
                    age INT,
                    email TEXT,
                    telephone TEXT,
                    ville TEXT,
                    statut TEXT,
                    created_at TIMESTAMP
                )
                """)

                cur.execute("""
                ALTER TABLE persons
                ADD COLUMN IF NOT EXISTS sexe TEXT
                """)
        conn.close()


# ================= APP =================
def main(page: ft.Page):

    init_db()

    page.title = "Freelance Secure PRO"
    page.window_width = 1400
    page.window_height = 900
    page.scroll = "auto"

    # ================= HOME =================
    def home():
        page.controls.clear()

        box = ft.Container(
            width=900,
            bgcolor="#000000aa",
            padding=30,
            border_radius=20,
            content=ft.Column([
                ft.Text(" BIENVENUE A FREELANCE SECURE", size=40, weight="bold", color="white"),
                ft.Text("Une Plateforme intelligente de recensement pour la population", color="white70"),
                ft.Row([
                    ft.ElevatedButton("S'inscrire", on_click=lambda e: collect()),
                    ft.OutlinedButton("ADMIN", on_click=lambda e: login())
                ], alignment="center")
            ], horizontal_alignment="center")
        )

        page.add(ft.Stack([
            ft.Image(src=BG, fit="cover", expand=True),
            ft.Column([box], alignment="center",
                      horizontal_alignment="center", expand=True)
        ], expand=True))

        page.update()

    # ================= COLLECT =================
    def collect():
        page.controls.clear()

        nom = ft.TextField(label="Nom")
        prenom = ft.TextField(label="Prénom")
        age = ft.TextField(label="Age")
        email = ft.TextField(label="Email")
        tel = ft.TextField(label="Téléphone")
        ville = ft.TextField(label="Ville")

        sexe = ft.Dropdown(label="Sexe", options=[
            ft.dropdown.Option("homme"),
            ft.dropdown.Option("femme")
        ])

        statut = ft.Dropdown(label="Statut", options=[
            ft.dropdown.Option("travailleur"),
            ft.dropdown.Option("non_travailleur")
        ])

        msg = ft.Text()

        def save(e):

            if not age.value or not age.value.isdigit():
                msg.value = "❌ Age invalide"
                msg.color = "red"
                page.update()
                return

            if not sexe.value or not statut.value:
                msg.value = "❌ Remplis tous les champs"
                msg.color = "red"
                page.update()
                return

            conn = get_conn()
            if not conn:
                msg.value = "❌ Connexion DB échouée"
                page.update()
                return

            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                        INSERT INTO persons(
                            nom, prenom, age, email,
                            telephone, ville, sexe, statut, created_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            nom.value,
                            prenom.value,
                            int(age.value),
                            email.value,
                            tel.value,
                            ville.value,
                            sexe.value,
                            statut.value,
                            datetime.now()
                        ))

                msg.value = "✅ Enregistré"
                msg.color = "green"

            except Exception as ex:
                msg.value = str(ex)
                msg.color = "red"

            finally:
                conn.close()

            page.update()

        page.add(ft.Stack([
            ft.Image(src=BG, fit="cover", expand=True),
            ft.Column([
                ft.Container(
                    width=600,
                    padding=20,
                    bgcolor="#ffffffee",
                    border_radius=20,
                    content=ft.Column([
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: home()),
                        ft.Text("Collecte", size=28, weight="bold"),
                        nom, prenom, age, email, tel, ville, sexe, statut,
                        ft.ElevatedButton("Enregistrer", on_click=save),
                        msg
                    ])
                )
            ], alignment="center", horizontal_alignment="center", expand=True)
        ], expand=True))

        page.update()

    # ================= LOGIN =================
    def login():
        page.controls.clear()

        u = ft.TextField(label="Utilisateur")
        p = ft.TextField(label="Mot de passe", password=True)
        msg = ft.Text(color="red")

        def go(e):
            if u.value == ADMIN_USER and p.value == ADMIN_PASS:
                dashboard()
            else:
                msg.value = "❌ Accès refusé"
                page.update()

        page.add(ft.Stack([
            ft.Image(src=BG, fit="cover", expand=True),
            ft.Column([
                ft.Container(
                    width=400,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    content=ft.Column([
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: home()),
                        ft.Text("Connexion Admin", size=28, weight="bold"),
                        u, p,
                        ft.ElevatedButton("Connexion", on_click=go),
                        msg
                    ])
                )
            ], alignment="center", horizontal_alignment="center", expand=True)
        ], expand=True))

        page.update()

    # ================= DASHBOARD =================
    def dashboard():
        page.controls.clear()

        conn = get_conn()
        if not conn:
            page.add(ft.Text("Erreur DB"))
            return

        with conn:
            with conn.cursor() as cur:

                cur.execute("SELECT COUNT(*) FROM persons")
                total = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM persons WHERE sexe='homme'")
                hommes = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM persons WHERE sexe='femme'")
                femmes = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM persons WHERE statut='travailleur'")
                travailleurs = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM persons WHERE statut='non_travailleur'")
                non_travailleurs = cur.fetchone()[0]

                cur.execute("""
                SELECT nom, prenom, ville, sexe, statut
                FROM persons
                ORDER BY id DESC
                """)
                data = cur.fetchall()

        conn.close()

        # ===== CARDS =====
        def card(title, value, color):
            return ft.Container(
                width=180,
                height=100,
                bgcolor=color,
                border_radius=15,
                padding=10,
                content=ft.Column([
                    ft.Text(title, color="white"),
                    ft.Text(str(value), size=26, weight="bold", color="white")
                ])
            )

        stats = ft.Row([
            card("Total", total, "#1e293b"),
            card("Hommes", hommes, "#2563eb"),
            card("Femmes", femmes, "#db2777"),
            card("Travailleurs", travailleurs, "#16a34a"),
            card("Non travailleurs", non_travailleurs, "#dc2626"),
        ], wrap=True, spacing=10)

        # ===== TABLE =====
        rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v))) for v in r]
            ) for r in data
        ]

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nom")),
                ft.DataColumn(ft.Text("Prénom")),
                ft.DataColumn(ft.Text("Ville")),
                ft.DataColumn(ft.Text("Sexe")),
                ft.DataColumn(ft.Text("Statut")),
            ],
            rows=rows
        )

        page.add(ft.Stack([
            ft.Image(src=BG, fit="cover", expand=True),

            ft.Row([
                # Sidebar
                ft.Container(
                    width=220,
                    bgcolor="#0f172a",
                    padding=20,
                    content=ft.Column([
                        ft.Text("ADMIN", size=28, color="white"),
                        ft.ElevatedButton("Accueil", on_click=lambda e: home()),
                    ])
                ),

                # Main
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Dashboard", size=30, weight="bold", color="white"),
                        stats,
                        ft.Divider(color="white"),
                        ft.Text("Liste des personnes", size=20, color="white"),
                        ft.Container(
                            bgcolor="white",
                            padding=10,
                            border_radius=10,
                            content=table
                        )
                    ])
                )
            ], expand=True)
        ], expand=True))

        page.update()

    home()


ft.app(target=main, view=ft.AppView.WEB_BROWSER)

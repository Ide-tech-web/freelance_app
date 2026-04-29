import streamlit as st
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime

# ================= CONFIG =================
DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = "5432"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

BG = "https://images.unsplash.com/photo-1492724441997-5dc865305da7"

# ================= STYLE =================
st.markdown(f"""
<style>
.stApp {{
    background-image: url("{BG}");
    background-size: cover;
}}

.block {{
    background: rgba(0,0,0,0.6);
    padding: 30px;
    border-radius: 15px;
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# ================= DB =================
def get_conn():
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            sslmode="require"  # IMPORTANT
        )
    except OperationalError as e:
        st.error(f"DB Error: {e}")
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
                    sexe TEXT,
                    statut TEXT,
                    created_at TIMESTAMP
                )
                """)
        conn.close()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ================= HOME =================
def home():
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.title("BIENVENUE A FREELANCE SECURE")
    st.write("Plateforme intelligente de recensement")

    col1, col2 = st.columns(2)
    if col1.button("S'inscrire"):
        st.session_state.page = "collect"

    if col2.button("ADMIN"):
        st.session_state.page = "login"

    st.markdown('</div>', unsafe_allow_html=True)

# ================= COLLECT =================
def collect():
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("Collecte")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    age = st.text_input("Age")
    email = st.text_input("Email")
    tel = st.text_input("Téléphone")
    ville = st.text_input("Ville")

    sexe = st.selectbox("Sexe", ["", "homme", "femme"])
    statut = st.selectbox("Statut", ["", "travailleur", "non_travailleur"])

    if st.button("Enregistrer"):

        if not age.isdigit():
            st.error("Age invalide")
            return

        if not sexe or not statut:
            st.error("Remplis tous les champs")
            return

        conn = get_conn()
        if not conn:
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
                        nom, prenom, int(age), email,
                        tel, ville, sexe, statut,
                        datetime.now()
                    ))

            st.success("Enregistré ✅")

        except Exception as e:
            st.error(str(e))

        finally:
            conn.close()

    if st.button("Retour"):
        st.session_state.page = "home"

    st.markdown('</div>', unsafe_allow_html=True)

# ================= LOGIN =================
def login():
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("Connexion Admin")

    u = st.text_input("Utilisateur")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.page = "dashboard"
        else:
            st.error("Accès refusé ❌")

    if st.button("Retour"):
        st.session_state.page = "home"

    st.markdown('</div>', unsafe_allow_html=True)

# ================= DASHBOARD =================
def dashboard():
    st.title("Dashboard")

    conn = get_conn()
    if not conn:
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
            FROM persons ORDER BY id DESC
            """)
            data = cur.fetchall()

    conn.close()

    # ===== STATS =====
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", total)
    col2.metric("Hommes", hommes)
    col3.metric("Femmes", femmes)
    col4.metric("Travailleurs", travailleurs)
    col5.metric("Non travailleurs", non_travailleurs)

    # ===== TABLE =====
    st.subheader("Liste des personnes")
    st.table(data)

    if st.button("Retour"):
        st.session_state.page = "home"

# ================= ROUTER =================
init_db()

if st.session_state.page == "home":
    home()
elif st.session_state.page == "collect":
    collect()
elif st.session_state.page == "login":
    login()
elif st.session_state.page == "dashboard":
    dashboard()

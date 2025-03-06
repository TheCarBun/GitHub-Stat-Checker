import streamlit as st
from streamlit import session_state as sst
from utils.fetch_github_data import fetch_star_count

TOKEN = st.secrets["token"]

def base_ui():
    """
    ### Sets up the base user interface for the Streamlit application.

    This function performs the following tasks:
    1. Configures the Streamlit page settings.
    2. Initializes the Streamlit session state.
    3. Displays the title bar and input fields.
    4. Creates a sidebar with a form.
    """

    # Streamlit Page Config
    page_config()

    # Initialise streamlit session state
    initialize_sst()

    # Title and input
    title_bar()

    with st.sidebar:
        form() # Streamlit Form

        if sst.username and sst.token and sst.button_pressed:
            nav_ui() # Sidebar navigation menu

        # how_to_use()
        promo()


def page_config():
    """
    ### Configures the Streamlit page settings.

    This function sets the page title, icon, layout, and menu items for the Streamlit app.
    The app is designed to track GitHub contributions and provide insights into user activity.

    Menu Items:
        - About: Provides information about the app and its developers.
        - Report a bug: Link to the GitHub issues page for reporting bugs.
    """

    st.set_page_config(
        page_title = "GitHub Stats",
        page_icon = "./static/icon.png",
        layout = "wide",
        menu_items={
            "About": """
            This is a Streamlit app that tracks your GitHub contributions and provides insights into your activity.  
            Built by [:red[TheCarBun]](https://github.com/TheCarBun/) & [:red[Pakagronglb]](https://github.com/pakagronglb)  
            GitHub: [:green[GitHub-Stats]](https://github.com/TheCarBun/GitHub-Stat-Checker)
            """,
            
            "Report a bug": "https://github.com/TheCarBun/GitHub-Stat-Checker/issues",
        }
    )

def initialize_sst():
    """
    ### Initialize the session state with default values if they are not already set.
    This function checks if certain keys are present in the session state (sst).

    If any of these keys are missing, it initializes them with default values:
    - 'username': an empty string
    - 'user_token': an empty string
    - 'token_present': False
    - 'button_pressed': False
    """

    # Initializing session state
    if 'username' not in sst:
        sst.username = ''
    if 'user_token' not in sst:
        sst.user_token = ''
    if 'token_present' not in sst:
        sst.token_present = False
    if 'button_pressed' not in sst:
        sst.button_pressed = False

def title_bar():
    """
    ### Creates a title bar for the Streamlit UI with the title "GitHub Stats" and a star button.

    The title bar consists of two columns:
    - The first column displays the title "GitHub Stats".
    - The second column displays a button with the current star count of the GitHub repository.

    The star button links to the GitHub repository and encourages users to give a star to the repository.
    """

    title_col, star_col = st.columns([8.5,1.5], vertical_alignment="bottom")
    title_col.title("GitHub Stats")
    stars = fetch_star_count()
    star_col.link_button(f"⭐ Star :orange[(**{stars}**)]", 
                        "https://github.com/TheCarBun/GitHub-Stat-Checker", 
                        help=f"Give a star to this repository on GitHub. Current stars: {stars}",
                        use_container_width=True)

def form():
    """
    ### Creates a form in a Streamlit container for GitHub username and optional personal access token input.

    The form includes:
    - A text input for the GitHub username.
    - A toggle to indicate if the user has a GitHub Access Token.
    - A conditional text input for the GitHub Personal Access Token if the toggle is enabled.
    - A button to trigger the analysis.

    Updates the global state variables `sst.username`, `sst.token_present`, `sst.user_token`, `sst.token`, and `sst.button_pressed` based on user input.
    """

    form = st.container(border=True)
    sst.username = form.text_input("Enter GitHub Username:", value=sst.username)
    
    if form.toggle("I have a GitHub Access Token", value=sst.token_present, help="Toggle if you have a token. Create [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)"):
        sst.token_present = True
    else:
        sst.token_present = False
    
    # Add warning about token permissions if showing private contributions
    if sst.token_present:
        sst.user_token = form.text_input("Enter GitHub Personal Access Token:", value=sst.user_token, type="password")
        sst.token = sst.user_token
    else:
        sst.token = TOKEN
    
    if form.button("Analyze", type="primary"):
        sst.button_pressed = True

def how_to_use():
    """
    ### Displays an expander with instructions on how to use the GitHub stats checker tool.

    The expander contains a brief guide on:
    - Entering the GitHub username.
    - Viewing stats and predictions.
    - Exporting the data for further analysis.
    """

    with st.expander("❓ How to Use This Tool"):
        st.write("""
        This tool analyzes your GitHub activity and predicts future contributions.
        - Enter your GitHub username.
        - View your stats and predictions.
        - Export the data for further analysis.
        """)


def nav_ui():
    """
    ### Creates the navigation sidebar UI for the GitHub stats checker application.
    This function adds navigation links to the sidebar using Streamlit's `st.page_link` method.
    The sidebar contains links to the "Overview" and "Predictions" pages, each with an icon and a help tooltip.
    
    **Sidebar Links:**
    - Overview: Links to "app.py" with a star icon and a tooltip for checking GitHub stats and contributions.
    - Predictions: Links to "./pages/predictions.py" with a lightning bolt icon and a tooltip for predicting GitHub contributions.
    """

    with st.sidebar.container(border=True):
        col1, col2 = st.columns(2)
        col1.page_link(
            "app.py", 
            label="Overview", 
            icon="✨",
            help="ℹ️ Check your GitHub stats and contributions.",
            use_container_width=True
            )
        col2.page_link(
            "./pages/predictions.py", 
            label="Predictions", 
            icon="⚡",
            help="ℹ️ Predict your GitHub contributions.",
            use_container_width=True
            )

def promo():
    with open("static/sidebar.html", "r", encoding="UTF-8") as sidebar_file:
        sidebar_html = sidebar_file.read()
    st.html(sidebar_html)

def growth_stats(total_contributions:int, contribution_rate:int, active_days:int, total_days:int, percent_active_days:float, since:str):
    col1, col2 = st.columns(2)
    col1.metric(
        label=f"Total Contributions {since}", 
        value=f"{total_contributions} commits",
        delta=f"{contribution_rate:.2f} contributions/day",
        delta_color="inverse" if contribution_rate < 1 else "normal",
        border=True
        )
    
    col2.metric(
        label="Active Days", 
        value=f"{active_days}/{total_days} days",
        delta=f"{percent_active_days:.1f}% days active",
        delta_color="inverse" if percent_active_days < 8 else "normal",
        border=True
        )
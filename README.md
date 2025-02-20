
| Commits | Issues | Pull Requests | Forks & Stars |
|---------|--------|---------------| ------------- |
| ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/TheCarBun/GitHub-Stat-Checker) | ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-raw/TheCarBun/GitHub-Stat-Checker?color=green) | ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr-raw/TheCarBun/GitHub-Stat-Checker?color=green)  | ![GitHub forks](https://img.shields.io/github/forks/TheCarBun/GitHub-Stat-Checker?style=for-the-badge) |
|![GitHub last commit](https://img.shields.io/github/last-commit/TheCarBun/GitHub-Stat-Checker) | ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed-raw/TheCarBun/GitHub-Stat-Checker) | ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr-closed-raw/TheCarBun/GitHub-Stat-Checker)  | ![GitHub Repo stars](https://img.shields.io/github/stars/TheCarBun/GitHub-Stat-Checker?style=for-the-badge&color=yellow) |

# GitHub Stat Checker

GitHub Contribution Tracker is a **Streamlit** web application that visualizes GitHub user contributions with insightful metrics, charts, and achievements. This app uses the **GitHub GraphQL API** to fetch and display data about a user's contribution history, enabling users to track and analyze their growth.

**ℹ️  _Now predicts user contribution over a year using previous year's contribution data_**

![image](https://github.com/user-attachments/assets/c3ed1d8b-4351-4f5c-955d-442b2f14ca54)

## Features
<details>
<summary><b>User Stats Overview</b></summary><br>

- **User Stats**:
  - Total contributions across all repositories _(Now shows no. of private and public commits)_.
  - Highest contributions in a single day _(Now shows date)_.
  - Current streak of consecutive contribution days.
  - Longest streak of consecutive contribution days.
  - GitHub joining date, total no. of days on GitHub and no. of active days.

- **Yearly Growth Stats**:
  - Total contribution in previous year
  - Rate of contribution
  - No. of activate days
  - Percentage of days active in the year
  - Same for current year for comparison

- **Visualizations**:
  - **Contributions Over Time**: A line chart showing daily contributions.
  - **Yearly Growth**: A bar chart summarizing contributions year by year.
  - **Day-of-Week Analysis**: Contributions grouped by the day of the week.
  - **Weekday vs. Weekend Contributions**: A bar chart comparing contributions made on weekdays versus weekends.
  - **Programming Languages**: Pie chart and a table showing which programming languages are used and in how many repos

- **Achievements**:
  - Dynamic achievements unlocked based on contribution and streak activity, such as:
    - **"🔥 Streak Warrior"**: A streak of over 30 days.
    - **"💪 Commit Master"**: Total contributions exceeding 1000.

</details>

<details>
<summary><b>User Contribution Predictions</b></summary><br>

- **Predictions & Trends**:
  - **Contribution Rate Growth**: Growth in contribution rate compared to last year
  - **Predicted Contributions This Year**: Total predicted commits this year, if user continues to contribute at the same rate
  - **Predicted Active Days This Year**: Total predicted active days this year, if user continues to contribute at the same rate
- **Milestone Estimations**:
  
  Predicts for milestones `[100, 500, 1000, 2000, 5000, 10000]` contributions:
  - Number of days required to achive commit milestones
  - Date on which milestone will be achieved
</details>


## Installation

### Prerequisites

1. Python 3.7 or higher.
2. GitHub [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classi) with GraphQL API access.
3. Streamlit (`pip install streamlit`).

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/TheCarBun/GitHub-Stat-Checker.git
   cd GitHub-Stat-Checker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`).

---

## Usage

1. Enter your **GitHub Username**.
2. Provide a **GitHub Personal Access Token** (with `read:user` and `repo` scopes for GraphQL API access).
3. View detailed stats, visualizations, and achievements based on your contribution data.

### How to Generate a GitHub Personal Access Token

1. Go to [GitHub Developer Settings](https://github.com/settings/tokens).
2. Click on **Generate new token (classic)** or **Generate token** (for fine-grained).
3. Select the following scopes:
   - `repo`
   - `read:user`
4. Copy the generated token and use it in the app.

## Folder Structure

```
github-contribution-tracker/
├── github_stats.py         # Logic for fetching and processing GitHub contribution data.
├── app.py                  # Streamlit app for displaying the dashboard.
├── requirements.txt        # Python dependencies.
└── README.md               # Project documentation.
```

---

### Future Improvements

- Add achievements in form of badges.
- Include repository-specific stats (e.g., most active repositories).
- Display contributions grouped by month.
- Add user rankings for team or organization collaboration.

## Screenshots

<details>
<summary><b>Click to View Images 📷</b></summary><br>

![image](https://github.com/user-attachments/assets/4691bbb4-f544-4ac4-8fda-f1734d4f80e1)

![image](https://github.com/user-attachments/assets/b8c13eba-3218-4515-8e86-23d11b34310d)

![image](https://github.com/user-attachments/assets/e570ccd1-7b26-4c21-9649-28f0b15234df)

![image](https://github.com/user-attachments/assets/4d00a782-73ae-4051-afd9-b236831a4b24)

![image](https://github.com/user-attachments/assets/c221c971-c944-4c7c-8058-2b1e3afcf9c1)

</details>

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -m 'Add your feature'`.
4. Push to your fork: `git push origin feature/your-feature`.
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **[Streamlit](https://streamlit.io/)**: For building the interactive web application.
- **[GitHub GraphQL API](https://docs.github.com/en/graphql)**: For data fetching.

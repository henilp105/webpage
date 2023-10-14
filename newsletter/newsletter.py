import requests
from datetime import datetime, timedelta
import sys
import os


def fetch_prs(repo, access_token):
    def is_young_pr(created_at):
        one_month_ago = datetime.now() - timedelta(days=30)
        return created_at >= one_month_ago

    def is_wip_pr(created_at):
        two_month_ago = datetime.now() - timedelta(days=60)
        one_month_ago = datetime.now() - timedelta(days=30)
        return two_month_ago <= created_at < one_month_ago

    headers = {"Authorization": f"Bearer {access_token}"}

    params = {
        "state": "all",
        "per_page": 100,
    }
    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls", headers=headers, params=params
    )

    if response.status_code == 200:
        prs = response.json()

        young_prs = [
            pr
            for pr in prs
            if is_young_pr(datetime.fromisoformat(pr["created_at"][:-1]))
        ]
        wip_prs = [
            pr for pr in prs if is_wip_pr(datetime.fromisoformat(pr["created_at"][:-1]))
        ]

        if len(young_prs) > 0 or len(wip_prs) > 0:
            updates.append(f"\n\n## {repo}")
            updates.append(f"\n\nHere's what's new in the {repo} repo:\n")
            for pr in young_prs:
                updates.append(
                    f"\n- [#{pr['number']}](https://github.com/{repo}/pull/{pr['number']}): {pr['title']}"
                )

        if len(wip_prs) > 0:
            updates.append("\n\nWork in progress:\n")
            for pr in wip_prs:
                updates.append(
                    f"\n- [#{pr['number']}](https://github.com/{repo}/pull/{pr['number']}) (WIP): {pr['title']}"
                )

    else:
        print(
            f"Failed to fetch PRs. Status code: {response.status_code} {response.reason}"
        )


try:
    access_token = sys.argv[1]
except:
    print("Usage: python newsletter.py <access_token>")
    sys.exit(1)

current_date_time = datetime.now()

year = current_date_time.year
day = current_date_time.day
month = current_date_time.strftime("%B")
date = current_date_time.strftime("%B %d, %Y")

repos = [
    "fortran-lang/webpage",
    "fortran-lang/stdlib",
    "fortran-lang/stdlib-cmake-example",
    "fortran-lang/fpm",
    "fortran-lang/registry",
    "fortran-lang/fpm-docs",
    "fortran-lang/setup-fpm",
    "fortran-lang/fpm-haskell",
    "fortran-lang/fortran-lang.org",
    "fortran-lang/benchmarks",
    "fortran-lang/fortran-forum-article-template",
    "fortran-lang/fftpack",
    "fortran-lang/minpack",
    "fortran-lang/test-drive",
    "fortran-lang/vscode-fortran-support",
    "j3-fortran/fortran_proposals",
]

with open("newsletter/newsletter_template.md", "r") as f:
    newsletter = f.read()

updates = []
for repo in repos:
    fetch_prs(repo, access_token)

newsletter_data = ["{month}", "{date}", "{year}", "{yyyy_mm_dd}", "{projects}"]
for i in newsletter_data:
    newsletter = newsletter.replace(
        i,
        i.format(
            month=month,
            date=date,
            year=year,
            yyyy_mm_dd=f"{year}-{current_date_time.month}-{day}",
            projects="".join(updates),
        ),
    )


directory = "source/news/"
folder_path = os.path.join(directory, f"{year}")

if not os.path.exists(folder_path):
    os.mkdir(folder_path)

with open(folder_path + f"/{day}-{current_date_time.month}-Fortran-Newsletter-{month}-{year}.md", "w") as f:
    f.write(newsletter)

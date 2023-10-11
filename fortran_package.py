import yaml
import json
import requests
from pathlib import Path
from collections import Counter


def get_contributors(repo):
    info = requests.get(f"https://api.github.com/repos/{repo}/contributors").json()
    if "message" in info:
        raise Exception(info["message"])
    return [contributor["login"] for contributor in info]


def categorize_tags(package_index):
    categories = {
        "numerical": [],
        "io": [],
        "scientific": [],
        "examples": [],
        "interfaces": [],
        "graphics": [],
        "programming": [],
        "strings": [],
        "data_types": [],
        "libraries": [],
        "tags": [],
    }
    tags_count = Counter()

    for entry in package_index:
        try:
            for tag in entry.get("tags", "").split():
                tags_count[tag] += 1
        except KeyError:
            pass

        for category in entry.get("categories", "").split():
            if category in categories:
                categories[category].append(entry)

    # Get the top 50 tags
    top_tags = [tag for tag, _ in tags_count.most_common(50)]
    categories["tags"] = top_tags

    return categories

root = Path(__file__).parent
package_index_path = root / "data" / "package_index.yml"
learning_path = root / "data" / "learning.yml"

with open(package_index_path, "r") as f:
    fortran_index = yaml.safe_load(f)
with open(learning_path, "r") as f:
    conf = yaml.safe_load(f)

fortran_tags = categorize_tags(fortran_index)

conf["reference_books"] = conf["reference-books"]
conf["reference_courses"] = conf["reference-courses"]
conf["reference_links"] = conf["reference-links"]


with open(root / "_data" / "fortran_package.json", "w") as f:
    json.dump(fortran_tags, f)
with open(root / "_data" / "fortran_learn.json", "w") as f:
    json.dump(conf, f)

repositories = [
    "fortran-lang/fortran-lang.org",
    "fortran-lang/webpage",
    "fortran-lang/fpm",
    "fortran-lang/stdlib",
    "j3-fortran/fortran_proposals",
]

contributors = []
for repo in repositories:
    contributors.extend(get_contributors(repo))

contributors = list(set(contributors))
contributors.sort()

contributor_repo = {
    "repo": "fortran-lang",
    "contributor": contributors,
}

with open(root / "_data" / "contributor.json", "w") as f:
    json.dump(contributor_repo, f)
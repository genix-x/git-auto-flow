import typer

app = typer.Typer(help="GAF - Gestion Automatisée de Fonctionnalités")

# ------------------------------
# Commandes principales
# ------------------------------
@app.command()
def init():
    """Initialiser un nouveau projet."""
    typer.echo("Init (fonction encore vide)")


@app.command()
def release():
    """Créer une nouvelle release."""
    typer.echo("Release (fonction encore vide)")


# ------------------------------
# Groupe: branch
# ------------------------------
branch_app = typer.Typer(help="Gérer les branches")
app.add_typer(branch_app, name="branch")


@branch_app.command("pull-request")
def pull_request():
    """Créer une pull request (alias: pr)."""
    typer.echo("Pull request (fonction encore vide)")


# alias : `gaf branch pr`
@branch_app.command("pr", hidden=True)
def pr_alias():
    """Alias de pull-request."""
    pull_request()


# ------------------------------
# Groupe: issue
# ------------------------------
issue_app = typer.Typer(help="Gérer les issues")
app.add_typer(issue_app, name="issue")

# (tu peux ajouter tes commandes ici)


# ------------------------------
# Groupe: repo
# ------------------------------
repo_app = typer.Typer(help="Gérer les dépôts")
app.add_typer(repo_app, name="repo")


@repo_app.command()
def create():
    """Créer un dépôt."""
    typer.echo("Repo create (fonction encore vide)")


@repo_app.command()
def update():
    """Mettre à jour un dépôt."""
    typer.echo("Repo update (fonction encore vide)")


# ------------------------------
# Entrée principale
# ------------------------------
if __name__ == "__main__":
    app()

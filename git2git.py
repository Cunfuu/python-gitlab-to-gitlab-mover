import gitlab

# Set up the source GitLab instance
source_url = 'https://source-gitlab.example.com/'
source_token = 'your_source_token_here'
source_gl = gitlab.Gitlab(source_url, private_token=source_token)

# Set up the destination GitLab instance
destination_url = 'https://destination-gitlab.example.com/'
destination_token = 'your_destination_token_here'
destination_gl = gitlab.Gitlab(destination_url, private_token=destination_token)

# Get all groups from the source instance
groups = source_gl.groups.list(all=True)

# Iterate through each group
for group in groups:
    print(f"Processing group '{group.name}'...")

    # Create the group in the destination instance
    new_group = destination_gl.groups.create({
        'name': group.name,
        'path': group.path,
        'description': group.description
    })

    # Get all projects in the group
    projects = group.projects.list(all=True)

    # Iterate through each project
    for project in projects:
        print(f"    Processing project '{project.name}'...")

        # Create the project in the destination instance
        new_project = destination_gl.projects.create({
            'name': project.name,
            'description': project.description,
            'visibility': project.visibility,
            'namespace_id': new_group.id
        })

        # Set up mirroring for the project
        if project.mirror:
            new_project.mirror_on_push = True
            new_project.mirror_trigger_builds = True
            new_project.mirror_overwrites_diverged_branches = True
            new_project.mirror = True
            new_project.mirror_user_id = destination_gl.user.id
            new_project.mirror_interval = project.mirror_interval
            new_project.save()

        # Push the repository to the destination instance
        source_repo = source_gl.projects.get(project.id).repository
        destination_repo = destination_gl.projects.get(new_project.id).repository
        destination_repo.create_from_template(source_repo)

print("Done!")

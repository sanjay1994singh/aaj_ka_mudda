def save_google_profile_data(backend, user, response, *args, **kwargs):
    if backend.name != 'google-oauth2' or not user:
        return

    changed_fields = []

    picture = response.get('picture')
    if picture and not user.google_avatar_url:
        user.google_avatar_url = picture
        changed_fields.append('google_avatar_url')

    email = response.get('email')
    if email and not user.email:
        user.email = email
        changed_fields.append('email')

    first_name = response.get('given_name')
    if first_name and not user.first_name:
        user.first_name = first_name
        changed_fields.append('first_name')

    last_name = response.get('family_name')
    if last_name and not user.last_name:
        user.last_name = last_name
        changed_fields.append('last_name')

    if changed_fields:
        user.save(update_fields=changed_fields)

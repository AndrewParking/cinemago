from datetime import datetime
from schematics.models import Model
from schematics.types import StringType, URLType, FloatType, IntType
from schematics.types.compound import ListType
from schematics.exceptions import ValidationError
from .models import Genre, Film


class GenreForm(Model):
    name = StringType(required=True, min_length=3, max_length=64)

    def validate_name(self, data, value):
        genre = Genre.query.filter_by(name=value).first()
        if genre is not None:
            raise ValidationError('Genre with such a name already exists.')
        return value

    class Options:
        serialize_when_none = False


class FilmForm(Model):
    name = StringType(required=True, min_length=3, max_length=64)
    description = StringType(min_length=3)
    cover_url = URLType(verify_exists=True)
    kp_rate = FloatType(min_value=0, max_value=10)
    imdb_rate = FloatType(min_value=0, max_value=10)
    duration = IntType(min_value=3)
    country = StringType(min_length=3, max_length=64)
    year = IntType(min_value=1895, max_value=datetime.utcnow().year)
    genres = ListType(IntType, min_size=1)

    def validate_name(self, data, value):
        film = Film.query.filter_by(name=value).first()
        if film is not None:
            raise ValidationError('Film with such a name already exists.')
        return value

    def validate_genres(self, data, value):
        if value:
            for i in value:
                genre = Genre.query.get(i)
                if genre is None:
                    raise ValidationError('There is no genre with such id: {id}'\
                        .format(id=i))
        return value

    def to_native(self, *args, **kwargs):
        data = super(FilmForm, self).to_native(*args, **kwargs)
        genres_ids = data.pop('genres', None)
        if genres_ids:
            genres = []
            for i in genres_ids:
                genre = Genre.query.get(i)
                genres.append(genre)
            data['genres'] = genres
        return data

    class Options:
        serialize_when_none = False

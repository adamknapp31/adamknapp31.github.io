import bubba_ML_v2

predict = bubba_ML_v2.Model()
movies = bubba_ML_v2.Movies()

print(predict.predictTopMovies(123, movies))

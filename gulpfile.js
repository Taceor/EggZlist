'use strict';

var gulp = require('gulp'),
    gutil = require('gulp-util'),
    sass = require('gulp-sass');

gulp.task('sass', function() {
  return gulp.src('app/source/scss/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('app/static/css'));
});

gulp.task('default', ['sass'], function() {
  gulp.watch('app/source/scss/**/*.scss', ['sass']);
});
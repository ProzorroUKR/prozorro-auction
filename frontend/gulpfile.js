const gulp          = require('gulp'),
      notify        = require('gulp-notify'),
      del           = require('del'),
      concat        = require('gulp-concat'),
      util          = require('gulp-util'),
      vendorFiles   = require('gulp-main-bower-files'),
      minify        = require('gulp-minify'),
      gulpFilter    = require('gulp-filter'),
      source        = require('vinyl-source-stream'),
      cleanCSS      = require('gulp-clean-css'),
      fileinclude   = require('gulp-file-include'),
      uglify        = require('gulp-uglify'),
      rename        = require('gulp-rename'),
      fs            = require('fs'),
      less          = require('gulp-less'),
      lessAutoprefix = require('less-plugin-autoprefix'),
      merge         = require('merge-stream'),
      sourcemaps    = require('gulp-sourcemaps'),
      render        = require('gulp-nunjucks-render'),
      data          = require('gulp-data'),
      rev           = require('gulp-rev'),
      revReplace    = require('gulp-rev-replace'),
      revdel        = require('gulp-rev-delete-original');

function  interceptErrors(error) {
  let args = Array.prototype.slice.call(arguments);
  notify.onError({
    title: 'Compile Error',
    message: '<%= error.message %>'
  }).apply(this, args);
  this.emit('end');
}


const config = JSON.parse(fs.readFileSync('./config.json'));
const db_name = config.db_name || 'database';
const app_name = config.app_name || 'auction.js';
const devel = ('devel' in config) ? config.devel : true;
const main_css = config.main_css || 'bundle.css';


gulp.task('base:all', () => {
  return gulp.src(config.assets).pipe(gulp.dest(config.buildDir));
});


gulp.task('js:vendor',  () => {
  return gulp.src(config.js)
          .pipe(sourcemaps.init())
          .pipe(concat('vendor.js'))
          .pipe(sourcemaps.write())
          .pipe(gulp.dest(config.buildDir + '/static/js'));
});

gulp.task('js:tenders',  () => {
  return gulp.src(config.modules.tenders.js)
  .pipe(sourcemaps.init())
  .pipe(concat('tenders.js'))
  .pipe(sourcemaps.write())
  .pipe(gulp.dest(config.buildDir + '/static/js'));
});

gulp.task('js:index', () => {
  return gulp.src(config.modules.index.js)
    .pipe(concat('index.js'))
    .pipe(gulp.dest(config.buildDir + '/static/js'));
});

gulp.task('js:archive', () => {
  return gulp.src(config.modules.archive.js)
    .pipe(concat('archive.js'))
    .pipe(gulp.dest(config.buildDir + '/static/js'));
});

gulp.task('css:less', () => {
  let autoprefix = new lessAutoprefix({ browsers: ['last 2 versions'] });
  return gulp.src('src/assets/css/starter-template.less')
    .pipe(less({
      plugins: [autoprefix]
    }))
    .on('error', interceptErrors)
    .pipe(gulp.dest('src/assets/css/'));
});

gulp.task('css:all', ['css:less'], () => {
  return gulp.src(config.styles)
    .pipe(concat('all.css'))
    .pipe(cleanCSS({compatibility: 'ie11'}))
    .pipe(gulp.dest(config.buildDir + '/static/css'));
});

gulp.task('html:all', () => {
    return gulp.src('templates/*.html')
    .pipe(render({
      path: 'templates/',
      data: config,
    }))
    .pipe(gulp.dest(config.buildDir));

});

gulp.task('revision', ['base:all', 'js:vendor', 'js:tenders', 'js:index', 'js:archive',  'css:all', 'html:all'], function(){
  return gulp.src([config.buildDir + '/**/*.css', config.buildDir + '/**/*.js'])
    .pipe(rev())
    .pipe(gulp.dest(config.buildDir))
    .pipe(revdel())
    .pipe(rev.manifest())
    .pipe(gulp.dest(config.buildDir));
})

gulp.task('revreplace', ['revision'], function(){
  var manifest = gulp.src(config.buildDir + '/rev-manifest.json');

  return gulp.src(config.buildDir + '/*.html')
    .pipe(revReplace({manifest: manifest}))
    .pipe(gulp.dest(config.buildDir));
});

gulp.task('build', ['revreplace'], () => {
  return gulp.src(config.buildDir + '/**/*.*')
      .pipe(gulp.dest(config.outDir));
});

gulp.task('build:buildout', ['clean', 'build'], () => {
  return gulp.src(config.outDir + '/**/*.*')
      .pipe(gulp.dest(config.buildout_outDir));
})

gulp.task('default', ['build:buildout']);

gulp.task('clean', function () {
  del.sync([config.buildDir + '*/**', config.outDir + '*/**'], {force: true});
});

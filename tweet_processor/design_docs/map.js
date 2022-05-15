function (doc) {
    doc.tokens.split(' ').some(function (word) {
        if (['education', 'vce', 'vcaa', 'atar', 'unit', 'units', 'study', 'class', 'textbook', 'maths', 'english', 'school', 'schools', 'student', 'students', 'result', 'results', 'exam', 'exams', 'assignments', 'assignment'].includes(word)) {
            if (doc.sentiment == 'POSITIVE') {
                emit(doc.suburb_tag, 1);
            }
            else {
                emit(doc.suburb_tag, 0);
            }
        }
    });
}
const passageE = document.getElementById('inp');
const questionE = document.getElementById('question');
const button = document.getElementById('button');
const answerE = document.getElementById('answer');

const answer = async (model, inp, question) => {
    console.log(model);
    try {
        const answers = await model.findAnswers(question, inp);
        return answers[0].text
    } catch (e) {
        return false;
    }
}

const main = async () => {
    const model = await qna.load();

    button.onclick = async () => {
        let ans = await answer(model, passageE.value, questionE.value);
        if (!ans) {
            answerE.innerHTML = 'No answer found';
        } else {
            answerE.innerHTML = ans;
        }

    }
}

main();
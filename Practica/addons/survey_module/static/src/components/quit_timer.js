/** @odoo-module **/

import { Component, useState, xml, mount } from "@odoo/owl";

export default class QuestionTimer extends Component {
    static template = xml`<div>
        <p>Contador: <span t-esc="state.timeElapsed" /></p>
    </div>`;

    setup() {
        this.state = useState({ counter: 90, timeElapsed:"00:00" });
        this.timer = setInterval(() => {
            this.state.counter--;
            this.state.timeElapsed = this.formatSecondsToMMSS(this.state.counter);
            console.log(this.state.counter);
            if (this.state.counter === 0) clearInterval(this.timer);
        }, 1000);

        const placeholderElement = document.querySelector('#question_timer_place_holder');
        const surveyPropsJsonString = placeholderElement.dataset.surveyProps;


        if (surveyPropsJsonString) {
            const surveyProps = surveyPropsJsonString;
            console.log(surveyProps);
            console.log(surveyProps.survey) 
        }
    }

    willUnmount() {
        clearInterval(this.timer);
    }


    formatSecondsToMMSS(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;

        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }



}
mount(QuestionTimer, document.querySelector("#question_timer_place_holder"));
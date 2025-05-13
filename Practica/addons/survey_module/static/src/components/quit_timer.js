/** @odoo-module **/

import { Component, useState, xml, mount } from "@odoo/owl";

export default class QuestionTimer extends Component {
    static template = xml`<div>
        <p>Contador: <span t-esc="state.counter" /></p>
    </div>`;

    setup() {
        this.state = useState({ counter: 0, Date: new Date(). });
        this.timer = setInterval(() => {
            this.state.counter--;
            console.log(this.state.counter);
            if (this.state.counter === 0) clearInterval(this.timer);
        }, 1000);

        const placeholderElement = document.querySelector('#question_timer_place_holder');
        const surveyPropsJsonString = placeholderElement.dataset.surveyProps;


        if (surveyPropsJsonString) {
            const surveyProps = surveyPropsJsonString; // Convierte la cadena JSON a un objeto JavaScript
            console.log(surveyProps);
            console.log(surveyProps.survey) // Acceder a los datos
            // Ahora puedes pasar surveyProps a tu componente OWL
        }
    }

    willUnmount() {
        clearInterval(this.timer);
    }
}
mount(QuestionTimer, document.querySelector("#question_timer_place_holder"));
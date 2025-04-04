/** @odoo-module **/

import { ListRenderer } from '@web/views/list/list_renderer';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

class CustomOne2ManyRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.env = useService('env');  
    }

    // _onAddRecord() {
    //     console.log("Añadiendo un nuevo registro");

    //     if (this.props.record.data.suggested_answer_ids.length >= 2) {
    //         alert("Solo se permiten dos opciones");
    //         return; 
    //     }

    //     super._onAddRecord(...arguments);
    // }
}

registry.add('custom_one2many', CustomOne2ManyRenderer);

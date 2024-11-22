const BASE_URL = $('body').attr('url');
const USER_ID = $('body').attr('user_id');
const API_LINK = `${BASE_URL}edit_data`;
const SUBMIT_BUTTON = $('.save');

function validation(email_value, report_resource_value) {
    return validator.isEmail(email_value) && validator.isURL(report_resource_value);
}

async function save_data(email_value, report_resource_value) {
    SUBMIT_BUTTON.prop('disabled', true);

    try {
        const data = {
            'user_id': USER_ID,
            'email': email_value,
            'report_resource': report_resource_value
        }

        const headers = {}

        const response = await axios.post(
            API_LINK,
            data,
            { headers }
        )

        const { status, err_description } = await response.data;

        if (status === 'error') {
            alert(err_description)
        } else {
            alert('Дані успішно змінено!')
        }

    } catch (err) {
        alert(err.message);
    }

    SUBMIT_BUTTON.prop('disabled', false);
    return
}

$(document).ready(async () => {
    SUBMIT_BUTTON.off('click').on('click', async function(e) {
        e.preventDefault();
        let email_value = $('#email').val().replaceAll(' ', '');
        let report_resource_value = $('#report_resource').val().replaceAll(' ', '');
        
        if (validation(email_value, report_resource_value)) {
            await save_data(email_value, report_resource_value);
        }

        return;
    })
})
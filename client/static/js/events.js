"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderMsg(msg) {
    $("div.notification").html("<div class='alert alert-primary' role='alert'>" + msg + "</div>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function postEvent(event) {
    event.preventDefault();
    let data = {};
    let form = $("form[name='postEventForm']");
    data.name = $("input[name='eventName']").val();
    data.time = $("input[name='eventTime']").val();
    data.description = $("input[name='eventDesc']").val();
    data.location = $("input[name='eventLocation']").val();
    data.organization = $("input[name='eventOrg']").val();
    submitEvent(form.attr("action"), form.attr("method"), data, getSubmittedEvent);
}

function submitEvent(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

$(document).ready(function () {
    getResource("http://localhost:5000/eventhub/", renderSensors);
});
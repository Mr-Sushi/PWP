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
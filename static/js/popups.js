// popups.js - linked at the bottom of base.html with {% static 'js/popups.js' %}
// here we make the View, Edit and Delete icons on the records pages open a popup window instead of a new page.
// The popups are <dialog> elements in base.html. showModal() opens one over the page and close() hides it again.
// If JavaScript is turned off the icons are still normal links and forms, so the full pages keep working.

var recordPopup = document.querySelector("#record-popup");
var popupBody = document.querySelector("#popup-body");
var deletePopup = document.querySelector("#delete-popup");
// the delete form waiting for the user to click "Yes, delete"
var pendingDeleteForm = null;

// this function adds ?popup=1 to an address, so the view sends back only the popup content (no sidebar or top bar)
function popupAddress(address) {
    return address + (address.indexOf("?") === -1 ? "?popup=1" : "&popup=1");
}

// this function opens the popup and loads a View or Edit page into it
function openPopup(address) {
    popupBody.innerHTML = '<p class="popup-loading">Loading...</p>';
    if (!recordPopup.open) {
        recordPopup.showModal();
    }
    // fetch() asks the server for the page in the background, without leaving the current page
    fetch(popupAddress(address))
        .then(function (response) {
            // a redirect here means the login has expired, so we open the full page and let Django send the user to the login page
            if (response.redirected || !response.ok) {
                window.location.href = address;
                return null;
            }
            return response.text();
        })
        .then(function (html) {
            if (html !== null) {
                popupBody.innerHTML = html;
            }
        })
        .catch(function () {
            // if the request fails (e.g. the server is stopped) we fall back to opening the normal page
            window.location.href = address;
        });
}

// this function sends the Edit form from inside the popup
function sendPopupForm(form) {
    // FormData collects every field of the form, including the hidden csrf_token
    fetch(form.action, { method: "POST", body: new FormData(form), redirect: "manual" })
        .then(function (response) {
            // when the data is saved, edit_record_view answers with a redirect. redirect: "manual" lets us see that answer instead of following it.
            // We reload the page underneath, which closes the popup and shows the "updated successfully" message.
            if (response.type === "opaqueredirect") {
                window.location.reload();
                return null;
            }
            return response.text();
        })
        .then(function (html) {
            // otherwise the form had errors, and the view sent the form back with the errors under each field
            if (html !== null) {
                popupBody.innerHTML = html;
            }
        })
        .catch(function () {
            // if the request fails we send the form the normal way
            form.submit();
        });
}

// this function shows the "Are you sure?" popup for a delete form
function askBeforeDelete(form) {
    pendingDeleteForm = form;
    // data-confirm-delete holds the name of the record, e.g. "John Kato"
    document.querySelector("#delete-popup-text").textContent = "You are about to delete " + form.dataset.confirmDelete + ".";
    // if the View popup is open, close it so only the question is showing
    if (recordPopup.open) {
        recordPopup.close();
    }
    deletePopup.showModal();
}

// here we run all of the above only when the popups exist, i.e. when someone is logged in
if (recordPopup && deletePopup) {

    // one click listener for the whole page. It checks what was clicked, so it also works for icons and buttons that were loaded into the popup later.
    document.addEventListener("click", function (event) {
        // closest() finds the clicked element or the nearest parent with that attribute
        var popupLink = event.target.closest("a[data-popup]");
        if (popupLink) {
            // preventDefault() stops the browser from following the link to a new page
            event.preventDefault();
            openPopup(popupLink.getAttribute("href"));
            return;
        }
        var closeButton = event.target.closest("[data-popup-close]");
        if (closeButton) {
            closeButton.closest("dialog").close();
        }
    });

    // one submit listener for the whole page, for the Edit form in the popup and for every delete form
    document.addEventListener("submit", function (event) {
        var form = event.target;
        if (form.hasAttribute("data-popup-form")) {
            event.preventDefault();
            sendPopupForm(form);
        } else if (form.hasAttribute("data-confirm-delete")) {
            event.preventDefault();
            askBeforeDelete(form);
        }
    });

    // "Yes, delete" sends the waiting delete form. form.submit() sends it the normal way, so delete_record_view runs and the page shows its message.
    document.querySelector("#delete-popup-confirm").addEventListener("click", function () {
        if (pendingDeleteForm) {
            pendingDeleteForm.submit();
        }
    });

    // clicking the dark area outside a popup closes it (the click lands on the dialog itself, not on anything inside it)
    [recordPopup, deletePopup].forEach(function (dialog) {
        dialog.addEventListener("click", function (event) {
            if (event.target === dialog) {
                dialog.close();
            }
        });
    });
}

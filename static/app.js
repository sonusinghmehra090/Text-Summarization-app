document.getElementById("summary_form").addEventListener("submit",async (e) =>{
    e.preventDefault();

    // Get reference to elements 
    const dialogueInput = document.getElementById("textbox");
    const summaryText = document.getElementById("summary-text");
    const submitButton = e.target.querySelector("button");

    const dialogue = dialogueInput.value.trim();
    if (!dialogue){
        return;
    }
    // show processing message and disable button 
    summaryText.innerText="processing...";
    submitButton.disabled=true;

    try{
        // Send dialogue to backend 
        const response = await fetch("/summary/",{
            method: "POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({dialogue}),
        })
        if (!response.ok){
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        summaryText.innerText = data.summary || "No summary returned.";
    } catch (err){
        summaryText.innerText = 'Error : ${err.message}';
    } finally {
        submitButton.disabled = false;
    }
    console.log(data.summary);
});

const baseURL = "http://localhost:8000/api/upload/"
export async function BeRequest(fileName : File){

    const formData = new FormData()
    formData.append('file', fileName)
    try{
        const response = await fetch(baseURL,{
            method: "POST",
            body:formData
        })
        if(!response.ok){
            console.log('server error')
        }
        const result = response.json()
        return result
    }catch(error){
        console.log("Upload failed ", error)
    }
}


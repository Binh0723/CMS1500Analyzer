import { AnalysisResult } from "../src/CMS1500Analyzer"

const baseURL = "http://localhost:8000/api/question/"
export async function ChatRequest(message:string){
    try{
        const response = await fetch(baseURL,{
            method: "POST",
            body:message
        })
        if(!response.ok){
            console.log('server error')
        }
        const result = response.json()
        return result
    }catch(error){
        console.log("Answer question failed ", error)
    }
}

function buildGeminiPrompt(result: AnalysisResult): string {
    const errorList = result.errors
      .map(error => `- ${error.field}: ${error.message}`)
      .join('\n');
  
    return `You are an expert in CMS 1500. Give me the rules for the box that the user is facing. The errors are:\n${errorList}`;
  }

export async function InitialChatRequest(analysisResult : AnalysisResult){
    if(analysisResult.errors.length == 0){
        return "You are good to go";
    }
    console.group("inside inital chat request")
    const message = buildGeminiPrompt(analysisResult)
    try{
        const response = await fetch(baseURL,{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({ message })

        })
        if(!response.ok){
            console.log("server error");
            return "Sorry, something went wrong on the server.";        }
        const result = await response.json()
        const str_result = result.result.Message
        return str_result; 
    }catch(error){
        console.log("Answer question failed ", error)
    }
    
}


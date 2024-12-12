from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from main import process_story, generate_story, handle_sight_words, combine

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models with more specific validation
class ProcessStoryRequest(BaseModel):
    unknownSightWords: List[str] = Field(default_factory=list)
    storyChoice: str = Field(..., pattern="^[gi]$")  # must be 'g' or 'i'
    problemLetters: List[str] = Field(default_factory=list)
    storyInput: Optional[str] = None
    storyTopic: Optional[str] = None
    storyLength: Optional[int] = Field(None, ge=1)  # must be greater than or equal to 1
    readingLevel: int = Field(default=5, ge=1, le=12)  # between 1 and 12, defaults to 5
    characterName: str = Field(default="Max")

class DecodabilityRequest(BaseModel):
    text: str = Field(..., min_length=1)  # must not be empty
    problems: List[str] = Field(default_factory=list)

# Default sight words (moved from main.py)
default_sight_words = "a,at,any,many,and,on,is,are,the,was,were,it,am,be,go,to,out,been,this,come,some,do,does,done,what,who,you,your,both,buy,door,floor,four,none,once,one,only,pull,push,sure,talk,walk,their,there,they're,very,want,again,against,always,among,busy,could,should,would,enough,rough,tough,friend,move,prove,ocean,people,she,other,above,father,usually,special,front,thought,he,we,they,nothing,learned,toward,put,hour,beautiful,whole,trouble,of,off,use,have,our,say,make,take,see,think,look,give,how,ask,boy,girl,us,him,his,her,by,where,were,wear,hers,don't,which,just,know,into,good,other,than,then,now,even,also,after,know,because,most,day,these,two,already,through,though,like,said,too,has,in,brother,sister,that,them,from,for,with,doing,well,before,tonight,down,about,but,up,around,goes,gone,build,built,cough,lose,loose,truth,daughter,son"

@app.post("/api/process-story")
async def process_story_endpoint(request: ProcessStoryRequest):
    try:
        # Update sight_words
        global sight_words
        sight_words = handle_sight_words(default_sight_words, ','.join(request.unknownSightWords))
        print(f"request: {request}")
        problems = request.problemLetters 
        readingLevel = request.readingLevel
        if int(readingLevel) <= 1:
            maxsyllable = 2
        elif int(readingLevel) <= 3:
            maxsyllable = 3
        elif int(readingLevel) <= 5:
            maxsyllable = 4
        elif int(readingLevel) <= 7:
            maxsyllable = 5
        elif int(readingLevel) <= 9: 
            maxsyllable = 6
        else:
            maxsyllable = 10
        if request.storyChoice == 'g':
            # Generate story
            if not request.storyTopic or not request.storyLength:
                raise HTTPException(
                    status_code=400, 
                    detail="Story topic and length required for story generation"
                )
            
            story = generate_story(
                request.storyTopic, 
                problems, 
                request.characterName,
                request.readingLevel,
                request.storyLength
            )
        else:
            # Process input story
            if not request.storyInput:
                raise HTTPException(
                    status_code=400, 
                    detail="Story input required for processing"
                )
            
            story = request.storyInput
        
        print("\n--- Processing Without Grammar Correction ---")
        story = process_story(story, problems, maxsyllable, apply_correction=False, spellcheck=False, combined=False)

        print("\n--- Processing With Grammar Correction and Spell Check ---")
        story1 = process_story(story, problems, maxsyllable, apply_correction=True, spellcheck=True, combined=False)
        
        story = combine(story, story1, problems)

        processed_story = process_story(
                story, 
                request.problemLetters,
                maxsyllable,
                apply_correction=False,
                spellcheck=True,
                combined=False
        )

        # For input stories, calculate decodability immediately
        if request.storyChoice == 'i':
            
            decodability = process_story(
                processed_story,
                request.problemLetters,
                maxsyllable,
                apply_correction=False,
                spellcheck=False,
                combined=False,
                decodabilityTest=True
            )
            return {
                "success": True,
                "processedStory": processed_story,
                "decodability": decodability
            }
        else:
            return {
                "success": True,
                "generatedStory": processed_story
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/decodability")
async def get_decodability_endpoint(request: DecodabilityRequest):
    try:
        decodability = process_story(
            request.text,
            request.problems,
            10,
            apply_correction=False,
            spellcheck=False,
            combined=False,
            decodabilityTest=True
        )

        return {
            "success": True,
            "decodability": decodability
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 
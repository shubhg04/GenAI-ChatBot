import logging
from config import EVALUATOR_MODEL_NAME, evaluation_prompt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

evaluator_llm = ChatGroq(
    model = EVALUATOR_MODEL_NAME,
    temperature = 0.0
)

EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", evaluation_prompt),
    ("user", "User Input:\n{user_input}\n\nBot Response:\n{bot_response}")
])

evaluation_parser = StrOutputParser()

evaluation_chain = EVALUATION_PROMPT | evaluator_llm | evaluation_parser


class ResponseEvaluator:
    def evaluate(self, user_input, bot_response):
        try:
            raw_output = evaluation_chain.invoke({
                "user_input": user_input,
                "bot_response": bot_response
            }).strip()

            logger.info(f"evaluation_stage = raw_output raw_output: {raw_output}")

            score = "incorrect"
            reason = "Evaluation parsing failed."

            for line in raw_output.splitlines():
                cleaned_line = line.strip()

                if cleaned_line.lower().startswith("score:"):
                    score = cleaned_line.split(":", 1)[1].strip().lower()

                elif cleaned_line.lower().startswith("reason:"):
                    reason = cleaned_line.split(":", 1)[1].strip()

            valid_scores = {"correct", "partially_correct", "incorrect"}

            if score not in valid_scores:
                score = "incorrect"
                reason = "Evaluator returned an invalid score."

            return {
                "score": score,
                "reason": reason
            }

        except Exception as error:
            logger.exception(f"evaluation_stage = failed error: {str(error)}")
            return {
                "score": "incorrect",
                "reason": "Evaluation request failed."
            }
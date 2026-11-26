import os
import time
import datetime
from typing import List, Optional
from functools import cached_property
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
import openai

# Set your OpenAI API key (replace with your actual key)
os.environ["OPENAI_API_KEY"] = "paste api key"

# Example rubrics to use as structural templates
example_rubric_1 = """
Pontuação: 22 pontos
 
a)       Identificação dos Tipos de Ciclos (Total: 6 pontos)
 
·         **Descrição**: O estudante deve identificar corretamente os dois tipos principais de ciclos em Python: for e while.
·         **Pontuação**:
o   Cada ciclo corretamente identificado (3 pontos).
o   Se mencionar apenas um tipo (3 pontos).
o   Caso não mencione nenhum dos tipos ou utilize termos incorretos (0 pontos).
 
b)      Explicação do Funcionamento do Ciclo for (Total: 7 pontos)
 
·         **Iteração sobre dados estruturados (3 pontos)**:
 
o   Explicar que o ciclo for é utilizado para iterar sobre elementos de uma sequência estruturada, como listas, strings, tuplas (tuplos) ou intervalos numéricos.
o   Pontuação:
§  Descrição completa e correta (3 pontos).
§  Descrição parcial (2 pontos).
§  Muita informação incorreta ou ausência total da informação relevante (0 pontos).
 
·         **Número conhecido de iterações (4 pontos)**:
 
o   Explicar que o for é adequado para situações em que o número de iterações é conhecido de antemão ou depende da quantidade de elementos a serem percorridos.
o   Pontuação:
§  Descrição completa e correta (4 pontos).
§  Descrição parcial (2-3 pontos).
§  Muita informação incorreta ou ausência total da informação relevante (0 pontos).
 
c)       Explicação do Funcionamento do Ciclo while (Total: 7 pontos)
 
·         **Repetição baseada em uma condição lógica (3 pontos)**:
 
o   Explicar que o ciclo while repete a execução de um bloco de código enquanto uma condição for verdadeira.
o   Pontuação:
§  Descrição completa e correta (3 pontos).
§  Descrição parcial (2 pontos).
§  Muita informação incorreta ou ausência total da informação relevante (0 pontos).
 
·         **Desconhecimento do número de iterações (4 pontos)**:
 
o   Indicar que o while é mais útil quando o número de repetições não é conhecido antecipadamente e a execução depende de uma condição que deve ser verificada continuamente.
o   Pontuação:
§  Descrição completa e correta (4 pontos).
§  Descrição parcial (2-3 pontos).
§  Muita informação incorreta ou ausência total da informação relevante (0 pontos).
 
d)      Clareza e Coerência na Comparação entre for e while (Total: 2 pontos)
 
·         **Descrição**: O estudante deve indicar claramente a diferença fundamental entre os ciclos for e while.
 
o   O for é adequado para percorrer coleções ou um número pré-determinado de iterações, enquanto o while é baseado numa condição lógica e é mais flexível para cenários incertos.
 
·         **Pontuação**:
o   Comparação clara e coerente (2 pontos).
o   Comparação incompleta ou ambígua (1 ponto).
o   Ausência de comparação ou incoerência (0 pontos).
"""

example_rubric_2 = """
Pontuação Total: 8 pontos
 
·         Indicação de Verdadeiro ou Falso (3 pontos)
o   **Descrição**: O estudante deve indicar corretamente que a afirmação é falsa.
o   **Pontuação**:
                                                                                                   i.      Indicação correta de "Falso" (3 pontos).
                                                                                                 ii.      Indicação incorreta de "Verdadeiro" (0 pontos).
·         Justificação da Resposta (Total: 5 pontos)
o   Explicação sobre Imutabilidade (4 pontos)
                                                                                                   i.      **Descrição**: A justificação deve mencionar que strings em Python são imutáveis, ou seja, uma vez criada, a string não pode ser alterada.
                                                                                                 ii.      **Pontuação**:
1.       Descrição completa e correta (4 pontos).
2.       Descrição parcial ou ambígua (2-3 pontos).
3.       Muita informação incorreta ou ausência total da informação relevante (0 pontos).
o   Consequência da Imutabilidade (1 ponto)
                                                                                                   i.      **Descrição**: O estudante deve explicar que qualquer operação que pareça alterar uma string, como modificar um caractere, resulta na criação de uma nova string e não na modificação da original.
                                                                                                 ii.      **Pontuação**:
1.       Explicação correta e clara (1 ponto).
2.       Explicação ausente ou incorreta (0 pontos).
"""

# Custom Chat Model class for OpenAI
class CustomChatOpenAI(BaseChatModel):
    model_name: str
    temperature: float = 1.0  # Set default temperature to 1.0

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

    def __init__(self, model_name: str, temperature: float = 1.0):
        super().__init__(model_name=model_name, temperature=temperature)

    @cached_property
    def client(self):
        return openai.Client()

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> ChatResult:
        message_dicts = []
        for m in messages:
            if isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, AIMessage):
                role = "assistant"
            elif isinstance(m, SystemMessage):
                role = "system"
            else:
                role = "user"
            message_dicts.append({
                "role": role,
                "content": m.content
            })

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message_dicts,
            temperature=self.temperature,
            stop=stop,
            **kwargs
        )

        message = AIMessage(content=response.choices[0].message.content)
        gen = ChatGeneration(message=message)
        return ChatResult(generations=[gen])

    @property
    def _llm_type(self) -> str:
        return "custom_openai_chat"

# Templates
PONTUACAO_RULES_PROMPT_TEMPLATE = """
Você é um assistente de avaliação de respostas a questões de programação. A sua tarefa é gerar as regras de pontuação detalhadas para cada critério estruturado, garantindo que a soma dos pontos atribuídos às mini regras (subcritérios) seja exatamente igual à pontuação total do critério. As regras devem ser formuladas de forma geral e aplicável a qualquer questão textual.

Para cada critério, siga estas orientações:
1. Identifique os componentes essenciais que o aluno deve demonstrar na resposta.
2. Divida o critério em mini regras que cubram todos os elementos essenciais da resposta.
3. Atribua pontos a cada mini regra de forma que, ao somá-los, se obtenha o total definido para o critério.
4. Se o critério for de resposta binária (por exemplo, perguntas de sim/não ou múltipla escolha), defina apenas duas regras:
   - Resposta correta: atribua a pontuação total.
   - Resposta incorreta ou ausência da resposta: 0 pontos.
5. Se o critério for de resposta parcial (por exemplo, justificações ou explicações elaboradas), defina:
   - Resposta completa: atribua a pontuação total, indicando que o aluno mencionou todos os conceitos essenciais.
   - Resposta parcial: atribua uma pontuação entre 30% e 70% do total, especificando os conceitos essenciais que devem ser referidos para uma resposta completa.
   - Resposta incorreta ou ausência da resposta: 0 pontos.
6. Use uma linguagem clara, objetiva e técnica, sem adicionar requisitos além do que o critério exige.
7. Penalização por elementos desnecessários ou errados: Para cada critério, defina uma penalização entre -5% a -20% dos pontos desse critério se o aluno adicionar elementos que alterem o comportamento esperado ou introduzam confusão na resposta.

Exemplo para critério binário:
Critério: "Indicar se é possível ou não alterar o tamanho do array depois de declarado" (Total: 15 pontos)
- Resposta correta (não é possível alterar o tamanho do array): 15 pontos.
- Resposta incorreta ou ausência da informação: 0 pontos.
- Penalização: -3 pontos (20%) se o aluno incluir informações contraditórias ou confusas sobre a possibilidade de alterar o tamanho.

Exemplo para critério com resposta parcial:
Critério: "Justificar a resposta anterior referindo à alocação de memória" (Total: 25 pontos)
- Resposta completa: o aluno explica que a memória é alocada de forma estática e contínua, detalhando os riscos de aceder à memória fora dos limites. (25 pontos)
- Resposta parcial: o aluno menciona a alocação de memória, mas não detalha todos os conceitos essenciais, atribuindo entre 30% a 70% do total (ex.: 8 a 15 pontos).
- Resposta incorreta ou ausência da justificativa: 0 pontos.
- Penalização: até -5 pontos (20%) por adicionar informações incorretas sobre alocação de memória que possam confundir a avaliação.

A sua resposta deve apresentar, para cada critério, uma lista de mini regras que, juntas, somem exatamente à pontuação total do critério.

### Reasoning ###
Por favor, analise cada critério e divida-o em mini regras seguindo as orientações acima. Para cada mini regra, atribua uma pontuação proporcional à sua importância, garantindo que, ao somar todas as mini regras de um critério, o total seja igual à pontuação definida para esse critério.

### Final Answer ###
Forneça as regras de pontuação para cada critério estruturado, organizadas em mini regras com pontuações específicas.
"""

GENERATE_STRUCTURED_CRITERIA_FOR_TEXT_TEMPLATE = """
Você está a gerar critérios estruturados para a avaliação de uma questão de programação. Utilize as seguintes informações:
- Pergunta: {question}
- Pontuação total: {total_points} pontos.
- Exemplos de respostas:
{examples}

A sua tarefa é:
1. Analisar cuidadosamente o enunciado e os exemplos de respostas.
2. Se a questão for de múltipla escolha ou verdadeiro/falso (com apenas uma resposta correta), gere UM único critério de avaliação que contemple ambas as possibilidades, definindo a pontuação total para uma resposta correta e, se pertinente, uma faixa para respostas parciais.
3. Se a questão for de resposta aberta (texto), identifique os principais aspetos relativos aos conteúdos que devem ser avaliados na resposta e agrupe os requisitos inter-relacionados quando fizer sentido. Divida a avaliação em sub-itens que cubram os aspetos essenciais do conteúdo.
4. IMPORTANTE: Separe claramente os critérios de identificação (resposta direta a uma pergunta) dos critérios de justificação ou explicação. Evite sobrepor requisitos entre diferentes critérios.
5. Para cada sub-item ou critério, gere um título breve e preciso que resuma o conteúdo avaliado. O título deve ser um texto simples, sem caracteres adicionais.
6. Atribua pontos a cada sub-item ou critério de forma que a soma dos pontos seja exatamente igual à pontuação total da questão.
7. **Não inclua critérios relacionados com a clareza, organização, estilo da resposta, Justificação Lógicas dos Resultados. Apenas critérios relativos aos conteúdos.**
8. Escreva toda a resposta em português de Portugal.

Retorne os critérios estruturados como um único texto, no formato:
Título Breve 1 (X pontos);
Título Breve 2 (Y pontos);
...
Certifique-se de que os critérios reflitam uma avaliação equilibrada e agrupem adequadamente os requisitos do enunciado.

### Reasoning ###
Vamos analisar a questão e os exemplos de respostas para identificar os aspectos essenciais a serem avaliados.

### Final Answer ###
Forneça os critérios estruturados no formato solicitado.
"""

CONSENSUS_RUBRIC_PROMPT = """
Você é um especialista em avaliação educacional e está a analisar múltiplas versões de rubricas de avaliação para uma mesma questão. A sua tarefa é criar uma única rubrica consensual de alta qualidade, combinando os melhores elementos de cada versão.

Questão: {question_text}
Pontuação Total: {question_total_score} pontos

Aqui estão exemplos de rubricas bem estruturadas para OUTRAS questões (use-as apenas como exemplos de formato e abordagem, NÃO para conteúdo):

EXEMPLO 1:
{example_rubric_1}

EXEMPLO 2:
{example_rubric_2}

Rubricas para analisar:

RUBRICA 1:
{rubric_1}

RUBRICA 2:
{rubric_2}

RUBRICA 3:
{rubric_3}

Para criar a rubrica consensual, siga estas orientações:
1. Identifique os critérios que aparecem consistentemente em todas as rubricas
2. Selecione as descrições mais claras e completas de cada critério
3. Certifique-se de que a estrutura seja hierárquica e bem organizada
4. Mantenha o formato consistente com os exemplos fornecidos
5. Verifique se a soma total de pontos é exatamente {question_total_score}
6. Certifique-se de que a rubrica cubra todos os aspectos essenciais da questão
7. Mantenha descrições detalhadas para níveis de pontuação completa, parcial e nula

Por favor, forneça uma rubrica consensual final que seja clara, abrangente e justa para avaliar as respostas dos estudantes.
"""

def generate_structured_criteria(question_text, question_total_score, examples, llm):
    """Generate structured criteria using the provided model"""
    generate_criteria_template = PromptTemplate.from_template(GENERATE_STRUCTURED_CRITERIA_FOR_TEXT_TEMPLATE)
    criteria_chain = RunnableSequence(generate_criteria_template | llm | StrOutputParser())
    
    structured_criteria = criteria_chain.invoke({
        "question": question_text,
        "total_points": question_total_score,
        "examples": examples
    })
    
    # Extract final answer
    try:
        reasoning_section, answer_section = structured_criteria.split("### Final Answer ###")
        structured_criteria = answer_section.strip()
    except ValueError:
        print("Warning: Model did not follow expected format for structured criteria.")
        structured_criteria = structured_criteria.strip()
    
    return structured_criteria

def generate_rubric(question_text, structured_criteria, examples, context, question_total_score, llm):
    """Generate a single rubric using the provided model and criteria"""
    combined_prompt_template = PromptTemplate.from_template("""
Utilize as informações abaixo para gerar as regras de pontuação para cada critério estruturado da questão de programação.

Aqui estão exemplos de rubricas bem estruturadas para OUTRAS questões (use-as apenas como exemplos de formato e abordagem, NÃO para conteúdo):

Exemplo 1:
{example_rubric_1}

Exemplo 2:
{example_rubric_2}

Questão:
{question_text}

Contexto do Curso:
{context}

Critérios Estruturados:
{structured_criteria}

Exemplo(s) de Resposta:
{examples}

Pontuação Total da Questão:
{question_total_score}

Prompt para Regras de Pontuação:
{pontuacao_rules_prompt_template}

INSTRUÇÕES ADICIONAIS IMPORTANTES:
1. Avalie cada critério ESTRITAMENTE dentro de seus limites - não sobreponha avaliações entre critérios.
2. Para critérios de identificação binária (ex: se algo é possível ou não), avalie APENAS a identificação correta, sem incluir elementos de justificação.
3. Para critérios que avaliam justificações, considere APENAS os elementos explicativos, assumindo que a identificação já foi avaliada em outro critério.
4. Mantenha a avaliação clara, evitando duplicar requisitos entre critérios diferentes.
5. Observe atentamente os exemplos de respostas para entender o que cada critério deve avaliar independentemente.

Agora, utilizando APENAS a questão atual e mantendo uma ESTRUTURA semelhante (mas com conteúdo completamente diferente e relevante para a questão atual), gere regras de pontuação detalhadas para CADA um dos critérios estruturados listados.
""")
    
    combined_chain = RunnableSequence(combined_prompt_template | llm | StrOutputParser())
    
    response = combined_chain.invoke({
        "question_text": question_text,
        "structured_criteria": structured_criteria,
        "pontuacao_rules_prompt_template": PONTUACAO_RULES_PROMPT_TEMPLATE,
        "context": context,
        "examples": examples,
        "question_total_score": question_total_score,
        "example_rubric_1": example_rubric_1,
        "example_rubric_2": example_rubric_2
    })
    
    # Extract final answer
    try:
        reasoning_section, answer_section = response.split("### Final Answer ###")
        final_answer = answer_section.strip()
    except ValueError:
        print("Warning: Model did not follow expected format for rubric.")
        final_answer = response.strip()
    
    return final_answer

def generate_consensus_rubric(question_text, question_total_score, rubrics, llm_consensus):
    """Generate a consensus rubric from multiple candidate rubrics"""
    consensus_template = PromptTemplate.from_template(CONSENSUS_RUBRIC_PROMPT)
    consensus_chain = RunnableSequence(consensus_template | llm_consensus | StrOutputParser())
    
    response = consensus_chain.invoke({
        "question_text": question_text,
        "question_total_score": question_total_score,
        "example_rubric_1": example_rubric_1,
        "example_rubric_2": example_rubric_2,
        "rubric_1": rubrics[0],
        "rubric_2": rubrics[1],
        "rubric_3": rubrics[2]
    })
    
    return response

def save_to_file(content, prefix="rubric"):
    """Save content to a markdown file with timestamp as name"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_text_free_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"Content saved to {filename}")
    return filename

def main():
    # Dados da questão
    question_text = """
Considere a seguinte árvore binária de pesquisa (BST):

               48
            /     \
          31      66
        /   \    /   \
       20   39  54    72
      /  \
    13   27

a)	Explique, de forma teórica e geral, como funcionam os dois métodos de remoção de nós numa árvore binária de pesquisa: fusão e cópia;
b)	Apresente a estrutura final da árvore após a remoção do valor 31 utilizando:
    •	o método de remoção por fusão;
    •	o método de remoção por cópia.

    """

    question_total_score = 50
    examples = """
    Correct Answear 1:
    A remoção por fusão consiste em eliminar o nó a remover e ligar as suas duas subárvores diretamente. A subárvore esquerda sobe para o lugar do nó removido. Depois, o maior valor da subárvore esquerda é ligado ao início da subárvore direita, garantindo que a estrutura continua ordenada.
    A remoção por cópia faz-se copiando o maior valor da subárvore esquerda (ou o menor da direita) para o nó a remover. A seguir, o nó de onde se copiou o valor é eliminado. Este método é útil porque o nó copiado terá no máximo um filho, simplificando a remoção.

    Estrutura final da árvore após remoção por fusão:

           48
         /     \
        20      66
      /   \    /   \
    13    27  54    72
            \
            39

    Estrutura final da árvore após remoção por cópia:

            48
          /     \
        27       66
      /   \    /   \
     20   39  54    72
     /
    13
                

    Correct Answear 2:
    Na remoção por fusão, remove-se o nó e substitui-se pela subárvore esquerda. Depois, o maior valor dessa subárvore (máximo) liga-se como pai da subárvore direita. Este processo funde ambas as subárvores mantendo a ordem da BST. Na remoção por cópia, copia-se o maior valor da subárvore esquerda ou o menor da direita para o nó a remover. Em seguida, remove-se o nó original de onde foi copiado o valor, que é mais simples de remover por ter no máximo um filho.
    Por fusão:
    •	O 20 substitui o 31;
    •	O 27 liga-se ao 39.
    Por cópia:
    •	O 31 é substituído por 27.
    •	O nó original 27 é eliminado.

    """
    context = "Conteúdos e conceitos abordados nas aulas de programação em C++."

    # Initialize the models
    reasoning_model = CustomChatOpenAI(
        model_name="o3-mini",
        temperature=1.0  # Default for reasoning model
    )
    
    consensus_model = CustomChatOpenAI(
        model_name="gpt-4o-2024-11-20",
        temperature=0.1  # Low temperature for consistency
    )
    
    print("Generating structured criteria...")
    structured_criteria = generate_structured_criteria(
        question_text, 
        question_total_score, 
        examples, 
        reasoning_model
    )
    
    # Generate multiple candidate rubrics
    print("Generating candidate rubrics...")
    candidate_rubrics = []
    for i in range(3):  # Generate 3 candidate rubrics
        print(f"Generating candidate rubric {i+1}/3...")
        rubric = generate_rubric(
            question_text,
            structured_criteria,
            examples,
            context,
            question_total_score,
            reasoning_model
        )
        candidate_rubrics.append(rubric)
        # Add a small delay to ensure different outputs
        time.sleep(1)
    
    # Generate consensus rubric
    print("Generating consensus rubric...")
    consensus_rubric = generate_consensus_rubric(
        question_text,
        question_total_score,
        candidate_rubrics,
        consensus_model
    )
    
    # Create output content
    output_content = f"""# Rubric Generation Results

## Original Question
{question_text}

## Total Points
{question_total_score}

## Structured Criteria
{structured_criteria}

## Candidate Rubric 1
{candidate_rubrics[0]}

## Candidate Rubric 2
{candidate_rubrics[1]}

## Candidate Rubric 3
{candidate_rubrics[2]}

## Final Consensus Rubric
{consensus_rubric}
"""
    
    # Save to file
    saved_file = save_to_file(output_content)
    
    print(f"Complete process finished. Results saved to {saved_file}")

if __name__ == "__main__":
    main()
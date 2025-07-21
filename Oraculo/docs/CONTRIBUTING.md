# Arquitetura de software

> It doesn’t take a huge amount of knowledge and skill to get a program working. [...]
> Getting it right is another matter entirely.

\- Robert C. Martin, Clean Architecture

O Oráculo foi desenvolvido utilizando-se uma abordagem de desenvolvimento de software conhecida com Domain-Driven Design (DDD), que concentra-se na modelagem do domínio de negócios como o elemento central do projeto. Ela divide o sistema em diferentes camadas, como a camada de domínio, aplicação e infraestrutura, e utiliza conceitos como agregados, entidades, objetos de valor e repositórios para criar um modelo de domínio bem definido e eficaz. Isso ajuda a construir sistemas mais alinhados com os requisitos do negócio, facilitando a manutenção, a evolução e a compreensão do software.

<p align="center">
  <img src="https://raw.githubusercontent.com/NilavPatel/dotnet-onion-architecture/main/docs/dotnet-onion-architecture.png" />
</p>

A figura acima representa a dependência entre os elementos dessa arquitetura de software. Nada no círculo interno pode ter conhecimento sobre qualquer coisa no círculo externo. Em particular, o código no círculo interno não deve fazer referência ao nome de algo declarado no círculo externo, seja uma função, classe, variável ou qualquer outra entidade de software nomeada.
## Domínio 

O domínio é a parte central e fundamental do sistema de software, onde reside a lógica de negócios e as regras que são específicas do domínio em questão. O domínio contém, mas não se restringe a: 

1. **Entidades**: São objetos que têm identidades distintas e cujo estado pode mudar ao longo do tempo. As entidades representam os conceitos centrais do domínio e encapsulam a lógica de negócios relacionada a eles.
2. **Repositórios**: São interfaces ou classes responsáveis por fornecer acesso aos dados do domínio. Eles ocultam os detalhes de armazenamento e recuperação de dados, permitindo que o domínio permaneça desacoplado da infraestrutura de armazenamento.

## Aplicação

A camada de aplicação é responsável por coordenar a interação entre o domínio e a infraestrutura, além de fornecer interfaces para as interações com o sistema. A camada de aplicação inclui: 

1. **Serviços de Aplicação**: São classes que encapsulam a lógica de coordenação entre os objetos de domínio, tratando das regras de negócios que envolvem múltiplas entidades.
2. **Adaptadores de interface**: Conjunto de adaptadores que convertem dados do formato mais conveniente para os serviços, para o formato mais conveniente para alguma entidade externa, como o banco de dados ou a web.

## Infraestrutura 

A camada de infraestrutura lida com todos os detalhes relacionados à implementação técnica do sistema que não fazem parte do núcleo da lógica de negócios do domínio. A camada de infraestrutura inclui:

1. **Banco de Dados**: Esta camada lida com o armazenamento e recuperação de dados do domínio. Ela inclui sistemas de gerenciamento de banco de dados (como SQL, NoSQL, etc.), scripts de migração de dados e outras ferramentas relacionadas à persistência de dados.
2. **Comunicação Externa**: Abrange qualquer comunicação com sistemas externos, como integrações com serviços de terceiros, APIs externas, serviços de mensageria, entre outros.

# Estrutura do Oráculo

A estrutura da API Oráculo:

```
oraculo
├── app
│   ├── domain
│   │   └── entities
│   │       └── predictor.py
│   ├── application
│   │   ├── classification_service.py
│   │   ├── firewall_service.py
│   │   ├── messenger_service.py
│   │   └── package_service.py
│   ├── infrastructure
│   │   ├── adapters
│   │   │   ├── message_broker.py
│   │   │   └── pfsense_client.py
│   │   ├── database
│   │   │   └── in_memory_database.py
│   │   └── rest
│   │       ├── app.py
│   │       ├── controllers
│   │       │   └── package_controller.py
│   │       ├── static
│   │       │   ├── css
│   │       │   ├── images
│   │       │   └── js
│   │       └── templates
│   │           └── index.html
│   ├── interfaces
│   │   ├── repositories
│   │   │   └── package_repository.py
│   │   ├── messenger.py
│   │   └── rest_client.py
│   ├── data
│   │   ├── models
│   │   │   └── model.pkl
│   │   └── rules
│   │       └── block.json
│   ├── config.py
│   └── main.py
└── requirements.txt
```

## Domínio da aplicação

A aplicação depende de uma entidade Predictor que realiza a predição da natureza de uma pacote IP: benigno ou malicioso.

```python
class Predictor:
	
	def __init__(self):
		with open('app/data/models/model.pkl', 'rb') as f:
			model = pickle.load(f)
		
		self.__model = model
	
	def predict(self, X):
		return self.__model.predict(X)[0]
```

## Camada de aplicação

A camada de aplicação consiste em quatro serviços responsáveis pela classificação dos pacotes de rede, pela comunicação com a API do pfSense para criação de uma regra no firewall, pela recepção de mensagens de um message broker e pelo salvamento dos pacotes e suas classificações em um banco de dados em memória.
### Classificação
```python
class ClassificationService:
	
	def __init__(self, predictor: Predictor):
		self.__predictor = predictor
	
	def pre_processing(self, message):
		try:
			data = json.loads(message)
			temp = list(data.values())
			return temp[0], numpy.array([temp[1:]])
		
		except Exception:
			raise
	
	def classification(self, input_data):
		return self.__predictor.predict(input_data)
```
### Firewall
```python
class FirewallService:
	
    def __init__(self, pfsense_client: RESTClient):
        self.__pfsense_client = pfsense_client
	
    def __create_blocking_rule(self, ip):
        try:
            with open('app/data/rules/block.json') as f:
                rule = json.load(f)
                rule['src'] = ip
			
            return rule 
		
        except Exception as e:
            print(f'Error accessing rule file: {e}')
	
    def block_source_ip(self, ip):
        print(f'Creating blocking rule for source IP: {ip}')
        rule = self.__create_blocking_rule(ip)
        self.__pfsense_client.post(data=rule)
```
### Messenger
```python
class MessengerService:
	
    def __init__(self, messenger: Messenger, 
					   classification_service: ClassificationService,
					   firewall_service: FirewallService, 
					   package_service: PackageService):
        self.__messenger = messenger
        self.__classification_service = classification_service
        self.__firewall_service = firewall_service
        self.__package_service = package_service
	
    def __handle_message(self, ch, method, properties, body):
        try:
            message = body.decode('utf-8')
            ip, input_data = self.__classification_service.pre_processing(message)
            prediction = self.__classification_service.classification(input_data)
			
            if(prediction == 0): 
                self.__firewall_service.block_source_ip(ip)
                self.__package_service.create_package(ip)
		
        except Exception as e:
            print(f"Error processing message: {str(e)}")
	
    def consume_message(self, queue_name):
        self.__messenger.receive_message(queue_name, self.__handle_message)
```
### Banco de dados de pacotes
```python
class PackageService:
    
    def __init__(self, repository: PackageRepository):
        self.__db = repository
	
    def get_packages(self):
        return self.__db.get_all()
	
    def create_package(self, package_data):
        self.__db.create(package_data)
```

## Infraestrutura da aplicação

A camada de infraestrutura da aplicação implementa todas as classes abstratas contidas no diretório de interfaces. Dessa foma, ela contém as configurações dos componentes responsáveis pela comunicação com o message broker, pela comunicação com a API do pfSense e pela exposição de endpoints da API conforme padrão REST.

#!/usr/bin/env python3
"""
SpamExperts TUI Interface
Interface de texto interativa para gerenciar o SpamExperts
"""

import sys
import os
import requests
import json
from datetime import datetime
import getpass

class Colors:
    """Cores ANSI para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SpamExpertsTUI:
    def __init__(self):
        self.base_url = "https://api.antispamcloud.com/api"
        self.username = ""
        self.password = ""
        self.current_domain = ""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SpamExperts-TUI/1.0',
            'Accept': 'application/json'
        })
    
    def clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprime o cabeçalho da aplicação"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    SPAMEXPERTS TUI                           ║")
        print("║              Interface de Gerenciamento                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        if self.current_domain:
            print(f"{Colors.OKCYAN}Domínio atual: {Colors.BOLD}{self.current_domain}{Colors.ENDC}")
            print()
    
    def print_menu(self, options, title="Menu Principal"):
        """Imprime um menu com opções numeradas"""
        print(f"{Colors.OKBLUE}{Colors.BOLD}{title}{Colors.ENDC}")
        print("─" * len(title))
        
        for i, option in enumerate(options, 1):
            print(f"{Colors.OKGREEN}{i}.{Colors.ENDC} {option}")
        
        print(f"{Colors.WARNING}0.{Colors.ENDC} Voltar/Sair")
        print()
    
    def get_user_input(self, prompt, password=False):
        """Obtém entrada do usuário"""
        try:
            if password:
                return getpass.getpass(f"{Colors.OKCYAN}{prompt}: {Colors.ENDC}")
            else:
                return input(f"{Colors.OKCYAN}{prompt}: {Colors.ENDC}").strip()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Operação cancelada.{Colors.ENDC}")
            return None
    
    def show_error(self, message):
        """Mostra mensagem de erro"""
        print(f"{Colors.FAIL}❌ Erro: {message}{Colors.ENDC}")
    
    def show_success(self, message):
        """Mostra mensagem de sucesso"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def show_info(self, message):
        """Mostra mensagem informativa"""
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")
    
    def wait_for_key(self):
        """Aguarda o usuário pressionar uma tecla"""
        input(f"\n{Colors.WARNING}Pressione ENTER para continuar...{Colors.ENDC}")
    
    def login(self):
        """Realiza o login no sistema"""
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.BOLD}Login no SpamExperts{Colors.ENDC}")
        print("─" * 22)
        
        self.username = self.get_user_input("Usuário")
        if not self.username:
            return False
            
        self.password = self.get_user_input("Senha", password=True)
        if not self.password:
            return False
        
        # Teste de autenticação com endpoint correto
        try:
            test_url = f"{self.base_url}/domain/list"
            response = self.session.get(test_url, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                self.show_success("Login realizado com sucesso!")
                return True
            elif response.status_code == 401:
                self.show_error("Credenciais inválidas")
                return False
            else:
                self.show_error(f"Falha na autenticação (Status: {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
            return False
    
    def set_domain(self):
        """Define o domínio para trabalhar"""
        domain = self.get_user_input("Digite o domínio")
        if domain:
            self.current_domain = domain
            self.show_success(f"Domínio definido: {domain}")
        else:
            self.show_error("Domínio não pode estar vazio")
    
    def get_smarthost(self):
        """Obtém informações do smarthost/destination"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        try:
            # Endpoint correto para obter destination/smarthost
            url = f"{self.base_url}/destination/read"
            params = {'domain': self.current_domain}
            
            print(f"{Colors.OKCYAN}Consultando: {url}?domain={self.current_domain}{Colors.ENDC}")
            response = self.session.get(url, params=params, auth=(self.username, self.password), timeout=10)
            
            print(f"{Colors.OKCYAN}Status Code: {response.status_code}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Response Text: {response.text[:200]}...{Colors.ENDC}")
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        data = response.json()
                        print(f"\n{Colors.BOLD}Informações do Destination/Smarthost{Colors.ENDC}")
                        print("─" * 35)
                        print(f"Domínio: {Colors.OKCYAN}{self.current_domain}{Colors.ENDC}")
                        
                        # SpamExperts usa 'destination' ao invés de 'smarthost'  
                        destinations = data.get('destinations', [])
                        if destinations:
                            for i, dest in enumerate(destinations, 1):
                                print(f"Destination {i}: {Colors.OKGREEN}{dest.get('destination', 'N/A')}{Colors.ENDC}")
                                if 'port' in dest:
                                    print(f"  Porta: {Colors.OKGREEN}{dest['port']}{Colors.ENDC}")
                                if 'priority' in dest:
                                    print(f"  Prioridade: {Colors.OKGREEN}{dest['priority']}{Colors.ENDC}")
                        else:
                            print(f"Destination: {Colors.WARNING}Não configurado{Colors.ENDC}")
                            
                    except json.JSONDecodeError as je:
                        self.show_error(f"Resposta não é JSON válido: {str(je)}")
                        print(f"Resposta completa: {response.text}")
                else:
                    self.show_error("Resposta vazia do servidor")
                    
            else:
                self.show_error(f"Erro HTTP {response.status_code}")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def get_quarantine(self):
        """Lista e-mails em quarentena"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        try:
            # Endpoint correto para quarentena
            url = f"{self.base_url}/quarantine/list"
            params = {'domain': self.current_domain}
            
            print(f"{Colors.OKCYAN}Consultando: {url}?domain={self.current_domain}{Colors.ENDC}")
            response = self.session.get(url, params=params, auth=(self.username, self.password), timeout=10)
            
            print(f"{Colors.OKCYAN}Status Code: {response.status_code}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Response Text: {response.text[:200]}...{Colors.ENDC}")
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        data = response.json()
                        messages = data.get('messages', [])
                        
                        print(f"\n{Colors.BOLD}Quarentena - {self.current_domain}{Colors.ENDC}")
                        print("─" * (len(self.current_domain) + 15))
                        
                        if not messages:
                            self.show_info("Nenhum e-mail em quarentena.")
                        else:
                            print(f"Total de mensagens: {Colors.BOLD}{len(messages)}{Colors.ENDC}\n")
                            
                            for i, msg in enumerate(messages, 1):
                                print(f"{Colors.OKBLUE}{i}.{Colors.ENDC} {Colors.BOLD}De:{Colors.ENDC} {msg.get('sender', 'N/A')}")
                                print(f"   {Colors.BOLD}Para:{Colors.ENDC} {msg.get('recipient', 'N/A')}")
                                print(f"   {Colors.BOLD}Assunto:{Colors.ENDC} {msg.get('subject', 'Sem assunto')}")
                                
                                if 'date' in msg:
                                    print(f"   {Colors.BOLD}Data:{Colors.ENDC} {msg['date']}")
                                
                                if 'reason' in msg:
                                    print(f"   {Colors.BOLD}Motivo:{Colors.ENDC} {Colors.WARNING}{msg['reason']}{Colors.ENDC}")
                                
                                if 'message_id' in msg:
                                    print(f"   {Colors.BOLD}ID:{Colors.ENDC} {msg['message_id']}")
                                
                                print()
                                
                    except json.JSONDecodeError as je:
                        self.show_error(f"Resposta não é JSON válido: {str(je)}")
                        print(f"Resposta completa: {response.text}")
                else:
                    self.show_error("Resposta vazia do servidor")
                    
            else:
                self.show_error(f"Erro HTTP {response.status_code}")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def list_domains(self):
        """Lista todos os domínios na conta"""
        try:
            url = f"{self.base_url}/domain/list"
            
            print(f"{Colors.OKCYAN}Consultando domínios...{Colors.ENDC}")
            response = self.session.get(url, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        data = response.json()
                        domains = data.get('domains', [])
                        
                        print(f"\n{Colors.BOLD}Domínios na Conta{Colors.ENDC}")
                        print("─" * 18)
                        
                        if not domains:
                            self.show_info("Nenhum domínio encontrado.")
                        else:
                            print(f"Total: {Colors.BOLD}{len(domains)}{Colors.ENDC}\n")
                            
                            for i, domain in enumerate(domains, 1):
                                if isinstance(domain, dict):
                                    domain_name = domain.get('domain', str(domain))
                                    status = domain.get('status', 'unknown')
                                    color = Colors.OKGREEN if status == 'active' else Colors.WARNING
                                else:
                                    domain_name = str(domain)
                                    color = Colors.OKCYAN
                                
                                print(f"{Colors.OKBLUE}{i}.{Colors.ENDC} {color}{domain_name}{Colors.ENDC}")
                                
                    except json.JSONDecodeError as je:
                        self.show_error(f"Resposta não é JSON válido: {str(je)}")
                        print(f"Resposta completa: {response.text}")
                else:
                    self.show_error("Resposta vazia do servidor")
                    
            else:
                self.show_error(f"Erro HTTP {response.status_code}")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def release_quarantine_message(self):
        """Libera mensagem da quarentena"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        message_id = self.get_user_input("Digite o ID da mensagem para liberar")
        if not message_id:
            return
        
        try:
            url = f"{self.base_url}/quarantine/release"
            params = {
                'domain': self.current_domain,
                'message_id': message_id
            }
            
            print(f"{Colors.OKCYAN}Liberando mensagem ID: {message_id}...{Colors.ENDC}")
            response = self.session.post(url, params=params, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                self.show_success(f"Mensagem {message_id} liberada com sucesso!")
            else:
                self.show_error(f"Erro ao liberar mensagem (Status: {response.status_code})")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def delete_quarantine_message(self):
        """Remove mensagem da quarentena permanentemente"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        message_id = self.get_user_input("Digite o ID da mensagem para deletar")
        if not message_id:
            return
        
        confirm = self.get_user_input("Tem certeza? (s/N)").lower()
        if confirm != 's':
            self.show_info("Operação cancelada.")
            return
        
        try:
            url = f"{self.base_url}/quarantine/delete"
            params = {
                'domain': self.current_domain,
                'message_id': message_id
            }
            
            print(f"{Colors.WARNING}Deletando mensagem ID: {message_id}...{Colors.ENDC}")
            response = self.session.post(url, params=params, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                self.show_success(f"Mensagem {message_id} deletada permanentemente!")
            else:
                self.show_error(f"Erro ao deletar mensagem (Status: {response.status_code})")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def add_whitelist(self):
        """Adiciona email/domínio à whitelist"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        address = self.get_user_input("Digite o email ou domínio para whitelist")
        if not address:
            return
        
        try:
            url = f"{self.base_url}/whitelist/create"
            params = {
                'domain': self.current_domain,
                'address': address
            }
            
            print(f"{Colors.OKCYAN}Adicionando à whitelist: {address}...{Colors.ENDC}")
            response = self.session.post(url, params=params, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                self.show_success(f"'{address}' adicionado à whitelist!")
            else:
                self.show_error(f"Erro ao adicionar whitelist (Status: {response.status_code})")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def add_blacklist(self):
        """Adiciona email/domínio à blacklist"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        address = self.get_user_input("Digite o email ou domínio para blacklist")
        if not address:
            return
        
        try:
            url = f"{self.base_url}/blacklist/create"
            params = {
                'domain': self.current_domain,
                'address': address
            }
            
            print(f"{Colors.WARNING}Adicionando à blacklist: {address}...{Colors.ENDC}")
            response = self.session.post(url, params=params, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                self.show_success(f"'{address}' adicionado à blacklist!")
            else:
                self.show_error(f"Erro ao adicionar blacklist (Status: {response.status_code})")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def get_domain_stats(self):
        """Obtém estatísticas do domínio"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        try:
            url = f"{self.base_url}/domain/stats"
            params = {'domain': self.current_domain}
            
            print(f"{Colors.OKCYAN}Obtendo estatísticas...{Colors.ENDC}")
            response = self.session.get(url, params=params, auth=(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        data = response.json()
                        
                        print(f"\n{Colors.BOLD}Estatísticas - {self.current_domain}{Colors.ENDC}")
                        print("─" * (len(self.current_domain) + 16))
                        
                        stats = data.get('stats', {})
                        print(f"Emails processados hoje: {Colors.OKGREEN}{stats.get('processed_today', 'N/A')}{Colors.ENDC}")
                        print(f"Spam bloqueado hoje: {Colors.WARNING}{stats.get('spam_today', 'N/A')}{Colors.ENDC}")
                        print(f"Emails em quarentena: {Colors.OKCYAN}{stats.get('quarantine_count', 'N/A')}{Colors.ENDC}")
                        print(f"Últimas 24h - processados: {Colors.OKGREEN}{stats.get('processed_24h', 'N/A')}{Colors.ENDC}")
                        print(f"Últimas 24h - spam: {Colors.WARNING}{stats.get('spam_24h', 'N/A')}{Colors.ENDC}")
                        
                    except json.JSONDecodeError as je:
                        self.show_error(f"Resposta não é JSON válido: {str(je)}")
                        print(f"Resposta completa: {response.text}")
                else:
                    self.show_error("Resposta vazia do servidor")
                    
            else:
                self.show_error(f"Erro HTTP {response.status_code}")
                if response.text:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.show_error(f"Erro de conexão: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro inesperado: {str(e)}")
    
    def domain_info(self):
        """Mostra informações gerais do domínio"""
        if not self.current_domain:
            self.show_error("Nenhum domínio definido. Configure um domínio primeiro.")
            return
        
        print(f"\n{Colors.BOLD}Informações do Domínio{Colors.ENDC}")
        print("─" * 22)
        print(f"Domínio: {Colors.OKCYAN}{self.current_domain}{Colors.ENDC}")
        print(f"Usuário API: {Colors.OKCYAN}{self.username}{Colors.ENDC}")
        print(f"Base URL: {Colors.OKCYAN}{self.base_url}{Colors.ENDC}")
        print(f"Timestamp: {Colors.OKCYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    def domain_menu(self):
        """Menu de operações do domínio"""
        while True:
            self.clear_screen()
            self.print_header()
            
            options = [
                "Obter Destination/Smarthost",
                "Listar Quarentena",
                "Liberar da Quarentena",
                "Deletar da Quarentena", 
                "Estatísticas do Domínio",
                "Adicionar Whitelist",
                "Adicionar Blacklist",
                "Alterar Domínio"
            ]
            
            self.print_menu(options, f"Gerenciar Domínio: {self.current_domain}")
            
            choice = self.get_user_input("Escolha uma opção")
            
            if choice == '1':
                self.get_smarthost()
                self.wait_for_key()
            elif choice == '2':
                self.get_quarantine()
                self.wait_for_key()
            elif choice == '3':
                self.release_quarantine_message()
                self.wait_for_key()
            elif choice == '4':
                self.delete_quarantine_message()
                self.wait_for_key()
            elif choice == '5':
                self.get_domain_stats()
                self.wait_for_key()
            elif choice == '6':
                self.add_whitelist()
                self.wait_for_key()
            elif choice == '7':
                self.add_blacklist()
                self.wait_for_key()
            elif choice == '8':
                self.set_domain()
                self.wait_for_key()
            elif choice == '0':
                break
            else:
                self.show_error("Opção inválida!")
                self.wait_for_key()
    
    def main_menu(self):
        """Menu principal da aplicação"""
        while True:
            self.clear_screen()
            self.print_header()
            
            options = [
                "Listar Todos os Domínios",
                "Configurar Domínio",
                "Gerenciar Domínio Atual",
                "Reconectar (Novo Login)"
            ]
            
            self.print_menu(options)
            
            if not self.current_domain:
                self.show_info("Configure um domínio para começar!")
                print()
            
            choice = self.get_user_input("Escolha uma opção")
            
            if choice == '1':
                self.list_domains()
                self.wait_for_key()
            elif choice == '2':
                self.set_domain()
                self.wait_for_key()
            elif choice == '3':
                if self.current_domain:
                    self.domain_menu()
                else:
                    self.show_error("Configure um domínio primeiro!")
                    self.wait_for_key()
            elif choice == '4':
                if self.login():
                    self.wait_for_key()
                else:
                    self.wait_for_key()
            elif choice == '0':
                print(f"\n{Colors.OKGREEN}Até logo!{Colors.ENDC}")
                break
            else:
                self.show_error("Opção inválida!")
                self.wait_for_key()
    
    def run(self):
        """Executa a aplicação"""
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.BOLD}Bem-vindo ao SpamExperts TUI!{Colors.ENDC}")
        print()
        
        # Login inicial
        if not self.login():
            print(f"\n{Colors.FAIL}Não foi possível fazer login. Encerrando...{Colors.ENDC}")
            return
        
        self.wait_for_key()
        
        # Menu principal
        self.main_menu()

def main():
    """Função principal"""
    try:
        app = SpamExpertsTUI()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Aplicação encerrada pelo usuário.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro inesperado: {str(e)}{Colors.ENDC}")

if __name__ == "__main__":
    main()

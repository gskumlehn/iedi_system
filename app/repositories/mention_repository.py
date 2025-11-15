from typing import List, Optional
from datetime import datetime
from app.infra.bq_sa import get_session
from app.models.mention import Mention
from app.models.analysis_mention import AnalysisMention
from app.utils.uuid_generator import generate_uuid

class MentionRepository:
    """
    Repository para gerenciar menções (dados brutos da Brandwatch).
    
    Menções são armazenadas uma única vez e reutilizadas em múltiplas análises.
    O identificador único é a URL (não o brandwatch_id).
    
    Brandwatch pode retornar a URL em dois campos:
    - 'url': URL principal da menção
    - 'originalUrl': URL original (caso seja redirecionamento)
    
    Ao coletar dados, verificar ambos os campos e usar o primeiro preenchido.
    
    Cálculos IEDI específicos por banco são gerenciados via AnalysisMentionRepository.
    """

    def create(self, **kwargs) -> Mention:
        """
        Cria uma nova menção com dados brutos da Brandwatch.
        
        Args:
            **kwargs: Campos da menção (url, brandwatch_id, title, domain, etc.)
        
        Returns:
            Mention: Menção criada
        
        Raises:
            ValueError: Se o campo 'url' não for fornecido
        """
        if 'url' not in kwargs:
            raise ValueError("Campo 'url' é obrigatório para criar menção")
        
        session = get_session()
        if 'id' not in kwargs:
            kwargs['id'] = generate_uuid()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        
        mention = Mention(**kwargs)
        session.add(mention)
        session.commit()
        session.refresh(mention)
        return mention

    def find_by_url(self, url: str) -> Optional[Mention]:
        """
        Busca menção por URL (identificador único real).
        
        Args:
            url: URL da menção
        
        Returns:
            Mention ou None se não encontrada
        """
        session = get_session()
        return session.query(Mention).filter(
            Mention.url == url
        ).first()
    
    def find_by_brandwatch_id(self, brandwatch_id: str) -> Optional[Mention]:
        """
        Busca menção por brandwatch_id (ATENÇÃO: não é identificador único).
        
        Este método existe para compatibilidade, mas o brandwatch_id pode se repetir.
        Use find_by_url() para busca por identificador único.
        
        Args:
            brandwatch_id: ID da menção na Brandwatch API
        
        Returns:
            Mention ou None se não encontrada
        """
        session = get_session()
        return session.query(Mention).filter(
            Mention.brandwatch_id == brandwatch_id
        ).first()

    def find_or_create(self, url: str, **kwargs) -> Mention:
        """
        Busca menção existente por URL ou cria nova se não existir.
        
        Args:
            url: URL da menção (identificador único)
            **kwargs: Campos da menção (title, domain, brandwatch_id, etc.)
        
        Returns:
            Mention: Menção encontrada ou criada
        """
        existing = self.find_by_url(url)
        if existing:
            return existing
        
        kwargs['url'] = url
        return self.create(**kwargs)
    
    @staticmethod
    def extract_unique_url(mention_data: dict) -> str:
        """
        Extrai URL única da menção Brandwatch.
        
        Brandwatch pode retornar a URL em dois campos:
        - 'url': URL principal
        - 'originalUrl': URL original (redirecionamentos)
        
        Args:
            mention_data: Dados brutos da menção Brandwatch
        
        Returns:
            URL única (primeiro campo preenchido)
        
        Raises:
            ValueError: Se nenhum campo de URL estiver preenchido
        """
        url = mention_data.get('url') or mention_data.get('originalUrl')
        
        if not url:
            raise ValueError(
                f"Menção sem URL: {mention_data.get('id')} - "
                "Campos 'url' e 'originalUrl' vazios"
            )
        
        return url

    def find_by_domain(self, domain: str) -> List[Mention]:
        """
        Busca menções por domínio do veículo.
        
        Args:
            domain: Domínio do veículo (ex: 'valor.globo.com')
        
        Returns:
            Lista de menções do domínio
        """
        session = get_session()
        return session.query(Mention).filter(Mention.domain == domain).all()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Mention]:
        """
        Busca menções publicadas em um período.
        
        Args:
            start_date: Data inicial
            end_date: Data final
        
        Returns:
            Lista de menções no período
        """
        session = get_session()
        return session.query(Mention).filter(
            Mention.published_date >= start_date,
            Mention.published_date <= end_date
        ).all()

    def update(self, mention_id: str, **kwargs) -> Optional[Mention]:
        """
        Atualiza campos de uma menção existente.
        
        Args:
            mention_id: UUID da menção
            **kwargs: Campos a atualizar
        
        Returns:
            Mention atualizada ou None se não encontrada
        """
        session = get_session()
        mention = session.query(Mention).filter(Mention.id == mention_id).first()
        
        if not mention:
            return None
        
        for key, value in kwargs.items():
            if hasattr(mention, key):
                setattr(mention, key, value)
        
        mention.updated_at = datetime.now()
        session.commit()
        session.refresh(mention)
        return mention


class AnalysisMentionRepository:
    """
    Repository para gerenciar relacionamentos análise-menção-banco + cálculos IEDI.
    
    Cada registro representa uma combinação única de (análise, menção, banco)
    com seus respectivos cálculos IEDI.
    """

    def create(self, analysis_id: str, mention_id: str, bank_id: str, **kwargs) -> AnalysisMention:
        """
        Cria relacionamento análise-menção-banco com cálculos IEDI.
        
        Args:
            analysis_id: UUID da análise
            mention_id: UUID da menção
            bank_id: UUID do banco
            **kwargs: Campos de cálculo IEDI (iedi_score, numerator, etc.)
        
        Returns:
            AnalysisMention: Relacionamento criado
        """
        session = get_session()
        
        analysis_mention = AnalysisMention(
            analysis_id=analysis_id,
            mention_id=mention_id,
            bank_id=bank_id,
            created_at=datetime.now(),
            **kwargs
        )
        
        session.add(analysis_mention)
        session.commit()
        session.refresh(analysis_mention)
        return analysis_mention

    def find_by_analysis(self, analysis_id: str) -> List[AnalysisMention]:
        """
        Busca todos os relacionamentos de uma análise.
        
        Args:
            analysis_id: UUID da análise
        
        Returns:
            Lista de relacionamentos (análise + menção + banco + IEDI)
        """
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id
        ).all()

    def find_by_analysis_and_bank(self, analysis_id: str, bank_id: str) -> List[AnalysisMention]:
        """
        Busca relacionamentos de uma análise para um banco específico.
        
        Args:
            analysis_id: UUID da análise
            bank_id: UUID do banco
        
        Returns:
            Lista de relacionamentos (menções do banco naquela análise)
        """
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id,
            AnalysisMention.bank_id == bank_id
        ).all()

    def find_by_mention(self, mention_id: str) -> List[AnalysisMention]:
        """
        Busca todos os relacionamentos de uma menção (em quais análises foi usada).
        
        Args:
            mention_id: UUID da menção
        
        Returns:
            Lista de relacionamentos (análises que usam esta menção)
        """
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.mention_id == mention_id
        ).all()

    def find_by_key(self, analysis_id: str, mention_id: str, bank_id: str) -> Optional[AnalysisMention]:
        """
        Busca relacionamento específico pela chave primária composta.
        
        Args:
            analysis_id: UUID da análise
            mention_id: UUID da menção
            bank_id: UUID do banco
        
        Returns:
            AnalysisMention ou None se não encontrado
        """
        session = get_session()
        return session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id,
            AnalysisMention.mention_id == mention_id,
            AnalysisMention.bank_id == bank_id
        ).first()

    def update_iedi_scores(self, analysis_id: str, mention_id: str, bank_id: str, 
                          iedi_score: float, numerator: int, denominator: int, **kwargs) -> Optional[AnalysisMention]:
        """
        Atualiza cálculos IEDI de um relacionamento existente.
        
        Args:
            analysis_id: UUID da análise
            mention_id: UUID da menção
            bank_id: UUID do banco
            iedi_score: Score IEDI calculado
            numerator: Numerador da fórmula
            denominator: Denominador da fórmula
            **kwargs: Outros campos (title_verified, etc.)
        
        Returns:
            AnalysisMention atualizado ou None se não encontrado
        """
        session = get_session()
        analysis_mention = self.find_by_key(analysis_id, mention_id, bank_id)
        
        if not analysis_mention:
            return None
        
        analysis_mention.iedi_score = iedi_score
        analysis_mention.numerator = numerator
        analysis_mention.denominator = denominator
        
        for key, value in kwargs.items():
            if hasattr(analysis_mention, key):
                setattr(analysis_mention, key, value)
        
        session.commit()
        session.refresh(analysis_mention)
        return analysis_mention

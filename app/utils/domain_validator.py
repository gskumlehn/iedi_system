from urllib.parse import urlparse
from typing import Set, List, Dict
from app.infra.bigquery_sa import get_session
from app.models.media_outlet import MediaOutlet

class DomainValidator:
    
    _monitored_domains_cache: Set[str] = None
    
    @classmethod
    def load_monitored_domains(cls) -> Set[str]:
        if cls._monitored_domains_cache is not None:
            return cls._monitored_domains_cache
        
        with get_session() as session:
            outlets = session.query(MediaOutlet.domain).filter(MediaOutlet.active == True).all()
            cls._monitored_domains_cache = {outlet.domain for outlet in outlets}
        
        return cls._monitored_domains_cache
    
    @classmethod
    def extract_domain(cls, url: str) -> str:
        if not url:
            return None
        
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    
    @classmethod
    def is_monitored_domain(cls, url: str) -> bool:
        domain = cls.extract_domain(url)
        monitored_domains = cls.load_monitored_domains()
        return domain in monitored_domains
    
    @classmethod
    def validate_mentions(cls, mentions: List[Dict]) -> Dict:
        monitored_domains = cls.load_monitored_domains()
        
        valid_mentions = []
        invalid_mentions = []
        invalid_domains = set()
        
        for mention in mentions:
            url = mention.get('url', '')
            domain = cls.extract_domain(url)
            
            if domain in monitored_domains:
                valid_mentions.append(mention)
            else:
                invalid_mentions.append(mention)
                invalid_domains.add(domain)
        
        return {
            'valid': valid_mentions,
            'invalid': invalid_mentions,
            'invalid_domains': list(invalid_domains),
            'valid_count': len(valid_mentions),
            'invalid_count': len(invalid_mentions),
            'total_count': len(mentions)
        }
    
    @classmethod
    def clear_cache(cls):
        cls._monitored_domains_cache = None

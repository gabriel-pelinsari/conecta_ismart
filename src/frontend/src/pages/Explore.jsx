import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";

const Wrap = styled.main`
  min-height: 100vh;
  padding: 80px 24px 40px 24px;
  background: ${({ theme }) => theme.colors.bg};
`;

const Container = styled.div`
  width: ${({ theme }) => theme.sizes.containerMedium};
  max-width: 100%;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 32px;
`;

const UsersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 40px;
`;

const UserCard = styled.div`
  padding: 16px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const Avatar = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: ${({ $url, theme }) =>
    $url ? `url(${$url})` : theme.colors.outline};
  background-size: cover;
  background-position: center;
  margin-bottom: 12px;
`;

const Name = styled.h3`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
`;

const Meta = styled.p`
  margin: 0;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const UserId = styled.span`
  display: inline-block;
  background: ${({ theme }) => theme.colors.outline};
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-top: 8px;
  font-family: monospace;
`;

export default function Explore() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      
      // ✅ Chamar endpoint para listar usuários
      const response = await api.get("/profiles/users", {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      setUsers(response.data);
      console.log(`✅ ${response.data.length} usuários carregados`);
    } catch (err) {
      console.error("❌ Erro ao carregar usuários:", err);
      setError("Erro ao carregar usuários");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <Wrap><Container><Title>Carregando...</Title></Container></Wrap>;
  if (error) return <Wrap><Container><Title>{error}</Title></Container></Wrap>;

  return (
    <Wrap>
      <Container>
        <Title>Explore Alunos</Title>
        <UsersGrid>
          {users.map((user) => (
            <UserCard
              key={user.user_id}
              onClick={() => navigate(`/profile/${user.user_id}`)}
            >
              <Avatar
                $url={
                  user.photo_url?.startsWith("/media")
                    ? `http://localhost:8000${user.photo_url}`
                    : user.photo_url
                }
              />
              <Name>{user.full_name}</Name>
              {user.university && <Meta>📍 {user.university}</Meta>}
              {user.course && <Meta>📚 {user.course}</Meta>}
              <UserId>ID: {user.user_id}</UserId>
            </UserCard>
          ))}
        </UsersGrid>
      </Container>
    </Wrap>
  );
}